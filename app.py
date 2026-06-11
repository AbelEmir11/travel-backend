from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from config import Config
from models import db, Usuario, Alojamiento, Reserva, Actividad, Servicio
import json

app = Flask(__name__)
app.config.from_object(Config)

# Configurar expiración de tokens JWT (ej. 30 días para persistencia de sesión cómoda)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)

# Inicializar extensiones
CORS(app)
db.init_app(app)
jwt = JWTManager(app)

# Crear tablas automáticamente al inicio si no existen (ideal para facilidad en la entrega)
with app.app_context():
    db.create_all()


# ==========================================
# RUTAS DE AUTENTICACIÓN (EN ESPAÑOL)
# ==========================================

@app.route("/api/autenticacion/registro", methods=["POST"])
def registro():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos."}), 400
        
    nombre = datos.get("nombre")
    email = datos.get("email")
    password = datos.get("password")
    
    if not nombre or not email or not password:
        return jsonify({"error": "Por favor completa todos los campos obligatorios."}), 400
        
    # Verificar si el usuario ya existe
    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "El correo electrónico ya está registrado."}), 400
        
    # Crear usuario
    password_hash = generate_password_hash(password)
    nuevo_usuario = Usuario(nombre=nombre, email=email, password_hash=password_hash)
    
    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        # Generar token automáticamente al registrarse
        token_acceso = create_access_token(identity=str(nuevo_usuario.id))
        return jsonify({
            "mensaje": "Usuario registrado con éxito.",
            "token": token_acceso,
            "usuario": nuevo_usuario.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al registrar usuario: {str(e)}"}), 500


@app.route("/api/autenticacion/ingreso", methods=["POST"])
def ingreso():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos."}), 400
        
    email = datos.get("email")
    password = datos.get("password")
    
    if not email or not password:
        return jsonify({"error": "Falta email o contraseña."}), 400
        
    usuario = Usuario.query.filter_by(email=email).first()
    
    if not usuario or not check_password_hash(usuario.password_hash, password):
        return jsonify({"error": "Credenciales incorrectas."}), 401
        
    token_acceso = create_access_token(identity=str(usuario.id))
    return jsonify({
        "mensaje": "Ingreso exitoso.",
        "token": token_acceso,
        "usuario": usuario.to_dict()
    }), 200


@app.route("/api/autenticacion/perfil", methods=["GET"])
@jwt_required()
def obtener_perfil():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(int(usuario_id))
    if not usuario:
        return jsonify({"error": "Usuario no encontrado."}), 404
        
    return jsonify(usuario.to_dict()), 200


# ==========================================
# RUTAS DE ALOJAMIENTOS (EN ESPAÑOL)
# ==========================================

@app.route("/api/alojamientos", methods=["GET"])
@jwt_required(optional=True)
def listar_alojamientos():
    query = Alojamiento.query
    
    # Verificar si el usuario autenticado tiene permisos de administrador (comercial o general)
    identidad = get_jwt_identity()
    es_admin = False
    if identidad:
        usuario = Usuario.query.get(int(identidad))
        if usuario and usuario.rol in ["comercial", "general"]:
            es_admin = True
            
    # Si no es admin, solo listar alojamientos activos
    if not es_admin:
        query = query.filter_by(activo=True)
        
    # Obtener parámetros de filtro
    destino = request.args.get("destino")
    precio_max = request.args.get("precio_maximo")
    tipo = request.args.get("tipo")
    busqueda = request.args.get("busqueda")
    
    # Aplicar filtros si existen en la query string
    if destino and destino != "all":
        query = query.filter_by(ubicacion=destino)
        
    if tipo and tipo != "all":
        query = query.filter_by(tipo=tipo)
        
    if precio_max:
        try:
            query = query.filter(Alojamiento.precio <= int(precio_max))
        except ValueError:
            pass
            
    if busqueda:
        busqueda_fuzzy = f"%{busqueda}%"
        query = query.filter(
            (Alojamiento.titulo.like(busqueda_fuzzy)) |
            (Alojamiento.ubicacion.like(busqueda_fuzzy)) |
            (Alojamiento.descripcion.like(busqueda_fuzzy))
        )
        
    alojamientos = query.all()
    return jsonify([aloj.to_dict() for aloj in alojamientos]), 200


@app.route("/api/alojamientos/<id>", methods=["GET"])
def obtener_alojamiento(id):
    alojamiento = Alojamiento.query.get(id)
    if not alojamiento:
        return jsonify({"error": "Alojamiento no encontrado."}), 404
    return jsonify(alojamiento.to_dict()), 200


# ==========================================
# RUTAS DE RESERVAS (EN ESPAÑOL - PROTEGIDAS)
# ==========================================

@app.route("/api/reservas", methods=["POST"])
@jwt_required()
def crear_reserva():
    usuario_id = get_jwt_identity()
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos."}), 400
        
    alojamiento_id = datos.get("alojamiento_id")
    check_in_str = datos.get("check_in")
    check_out_str = datos.get("check_out")
    huespedes = datos.get("huespedes", 1)
    notes = datos.get("notes", "")
    
    if not alojamiento_id or not check_in_str or not check_out_str:
        return jsonify({"error": "Falta información obligatoria (alojamiento, check-in o check-out)."}), 400
        
    alojamiento = Alojamiento.query.get(alojamiento_id)
    if not alojamiento:
        return jsonify({"error": "El alojamiento seleccionado no existe."}), 404
        
    try:
        check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
        check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido. Utilice AAAA-MM-DD."}), 400
        
    # Validación lógica de fechas
    hoy = datetime.utcnow().date()
    if check_in < hoy:
        return jsonify({"error": "La fecha de check-in no puede ser anterior al día de hoy."}), 400
        
    if check_in >= check_out:
        return jsonify({"error": "La fecha de salida debe ser posterior a la fecha de entrada."}), 400
        
    # Calcular precio total (precio por noche * días + tasas de servicio de USD 40)
    dias = (check_out - check_in).days
    precio_total = (alojamiento.precio * dias) + 40
    
    nueva_reserva = Reserva(
        usuario_id=int(usuario_id),
        alojamiento_id=alojamiento_id,
        check_in=check_in,
        check_out=check_out,
        huespedes=int(huespedes),
        notes=notes,
        precio_total=precio_total,
        estado="pending"
    )
    
    try:
        db.session.add(nueva_reserva)
        db.session.commit()
        return jsonify({
            "mensaje": "Reserva solicitada con éxito.",
            "reserva": nueva_reserva.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al procesar la reserva: {str(e)}"}), 500


@app.route("/api/reservas", methods=["GET"])
@jwt_required()
def listar_reservas():
    usuario_id = get_jwt_identity()
    reservas = Reserva.query.filter_by(usuario_id=int(usuario_id)).order_by(Reserva.fecha_creacion.desc()).all()
    return jsonify([res.to_dict() for res in reservas]), 200


# ==========================================
# RUTAS DE ADMINISTRACIÓN COMERCIAL Y GENERAL
# ==========================================

@app.route("/api/alojamientos/<id>/visibilidad", methods=["PUT"])
@jwt_required()
def cambiar_visibilidad(id):
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(int(usuario_id))
    if not usuario or usuario.rol not in ["comercial", "general"]:
        return jsonify({"error": "No autorizado."}), 403
        
    datos = request.get_json()
    activo = datos.get("activo")
    if activo is None:
        return jsonify({"error": "Falta el campo activo."}), 400
        
    alojamiento = Alojamiento.query.get(id)
    if not alojamiento:
        return jsonify({"error": "Alojamiento no encontrado."}), 404
        
    alojamiento.activo = bool(activo)
    try:
        db.session.commit()
        return jsonify({"mensaje": "Visibilidad actualizada con éxito.", "alojamiento": alojamiento.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/alojamientos/<id>/promocion", methods=["PUT"])
@jwt_required()
def cambiar_promocion(id):
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(int(usuario_id))
    if not usuario or usuario.rol not in ["comercial", "general"]:
        return jsonify({"error": "No autorizado."}), 403
        
    datos = request.get_json()
    descuento = datos.get("descuento")
    if descuento is None:
        return jsonify({"error": "Falta el campo descuento."}), 400
        
    if descuento not in [0, 10, 25, 50]:
        return jsonify({"error": "Descuento inválido. Valores permitidos: 0, 10, 25, 50."}), 400
        
    alojamiento = Alojamiento.query.get(id)
    if not alojamiento:
        return jsonify({"error": "Alojamiento no encontrado."}), 404
        
    alojamiento.descuento = int(descuento)
    try:
        db.session.commit()
        return jsonify({"mensaje": "Promoción actualizada con éxito.", "alojamiento": alojamiento.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/usuarios", methods=["GET"])
@jwt_required()
def listar_usuarios_admin():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(int(usuario_id))
    if not usuario or usuario.rol != "general":
        return jsonify({"error": "Acceso denegado. Se requieren permisos de administrador general."}), 403
        
    usuarios = Usuario.query.order_by(Usuario.fecha_creacion.desc()).all()
    return jsonify([u.to_dict() for u in usuarios]), 200


@app.route("/api/admin/usuarios/<id>/rol", methods=["PUT"])
@jwt_required()
def cambiar_rol_usuario(id):
    usuario_id = get_jwt_identity()
    usuario_solicitante = Usuario.query.get(int(usuario_id))
    if not usuario_solicitante or usuario_solicitante.rol != "general":
        return jsonify({"error": "Acceso denegado. Se requieren permisos de administrador general."}), 403
        
    datos = request.get_json()
    nuevo_rol = datos.get("rol")
    if not nuevo_rol or nuevo_rol not in ["cliente", "comercial", "general"]:
        return jsonify({"error": "Rol inválido."}), 400
        
    usuario_destino = Usuario.query.get(int(id))
    if not usuario_destino:
        return jsonify({"error": "Usuario no encontrado."}), 404
        
    usuario_destino.rol = nuevo_rol
    try:
        db.session.commit()
        return jsonify({"mensaje": "Rol actualizado con éxito.", "usuario": usuario_destino.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/api/admin/estadisticas", methods=["GET"])
@jwt_required()
def obtener_estadisticas():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(int(usuario_id))
    if not usuario or usuario.rol != "general":
        return jsonify({"error": "Acceso denegado. Se requieren permisos de administrador general."}), 403
        
    # Obtener todas las reservas de la base de datos
    reservas = Reserva.query.all()
    alojamientos = Alojamiento.query.all()
    
    # 1. Calcular ingresos totales
    ingresos_totales = sum(r.precio_total for r in reservas)
    
    # 2. Total de reservas
    total_reservas = len(reservas)
    
    # 3. Reservas confirmadas vs pendientes
    confirmadas = len([r for r in reservas if r.estado == "confirmed"])
    
    # 4. Tasa de conversión simulada basada en visitas ficticias (ej. 1500 visitas)
    visitas_simuladas = 1500
    tasa_conversion = round((total_reservas / visitas_simuladas) * 100, 2) if total_reservas > 0 else 0.0
    
    # 5. Ingresos mes a mes (Año 2026 completo)
    ingresos_por_mes = {m: 0 for m in range(1, 13)}
    for r in reservas:
        if r.check_in.year == 2026:
            ingresos_por_mes[r.check_in.month] += r.precio_total
            
    ingresos_mensuales_lista = [
        {"mes": datetime(2026, m, 1).strftime("%B").capitalize()[:3], "monto": ingresos_por_mes[m]}
        for m in range(1, 13)
    ]
    
    # Traducir meses a español
    meses_es = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    for idx, item in enumerate(ingresos_mensuales_lista):
        item["mes"] = meses_es[idx]
        
    # 6. Comparativa mes actual vs mes anterior (Junio 2026 vs Mayo 2026)
    mes_actual = 6  # Asumimos junio 2026 según fecha del sistema
    mes_anterior = 5
    ingresos_mes_actual = ingresos_por_mes[mes_actual]
    ingresos_mes_anterior = ingresos_por_mes[mes_anterior]
    
    diferencia_porcentaje = 0
    if ingresos_mes_anterior > 0:
        diferencia_porcentaje = round(((ingresos_mes_actual - ingresos_mes_anterior) / ingresos_mes_anterior) * 100, 1)
    elif ingresos_mes_actual > 0:
        diferencia_porcentaje = 100.0  # Si el mes anterior fue 0 e ingresos actuales > 0, es 100% de aumento
        
    # 7. Reservas por provincia
    reservas_por_provincia = {}
    for r in reservas:
        if r.alojamiento:
            prov = r.alojamiento.provincia
            reservas_por_provincia[prov] = reservas_por_provincia.get(prov, 0) + 1
            
    # Convertir a lista de diccionarios para el gráfico
    reservas_por_provincia_lista = [
        {"provincia": prov, "cantidad": cant}
        for prov, cant in reservas_por_provincia.items()
    ]
    
    return jsonify({
        "ingresos_totales": ingresos_totales,
        "total_reservas": total_reservas,
        "reservas_confirmadas": confirmadas,
        "tasa_conversion": tasa_conversion,
        "ingresos_mes_actual": ingresos_mes_actual,
        "ingresos_mes_anterior": ingresos_mes_anterior,
        "diferencia_porcentaje": diferencia_porcentaje,
        "ingresos_mensuales": ingresos_mensuales_lista,
        "reservas_por_provincia": reservas_por_provincia_lista
    }), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)

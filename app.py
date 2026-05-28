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
def listar_alojamientos():
    query = Alojamiento.query
    
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


if __name__ == "__main__":
    app.run(port=5000, debug=True)

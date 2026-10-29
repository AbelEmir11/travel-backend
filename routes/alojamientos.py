from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import re
import uuid
from models import db, Alojamiento, Actividad, Servicio, Usuario
from utils.decorators import role_required, get_current_user

alojamientos_bp = Blueprint("alojamientos", __name__)

def generar_slug(texto):
    """Genera un slug simple y limpio para IDs de alojamientos."""
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', texto.lower()).strip('-')
    if not slug:
        slug = str(uuid.uuid4())[:8]
    return slug

@alojamientos_bp.route("", methods=["GET"])
@jwt_required(optional=True)
def listar_alojamientos():
    query = Alojamiento.query
    
    # Si el usuario es administrador comercial o general, ve tanto activos como inactivos
    identidad = get_jwt_identity()
    es_admin = False
    if identidad:
        usuario = Usuario.query.get(int(identidad))
        if usuario and usuario.rol in ["comercial", "general"]:
            es_admin = True
            
    if not es_admin:
        query = query.filter_by(activo=True)
        
    # Parametros de filtrado
    destino = request.args.get("destino")
    precio_max = request.args.get("precio_maximo")
    tipo = request.args.get("tipo")
    busqueda = request.args.get("busqueda")
    
    if destino and destino != "all":
        query = query.filter(
            (Alojamiento.ubicacion.ilike(f"%{destino}%")) | 
            (Alojamiento.provincia.ilike(f"%{destino}%"))
        )
        
    if tipo and tipo != "all":
        query = query.filter_by(tipo=tipo)
        
    if precio_max:
        try:
            query = query.filter(Alojamiento.precio <= int(precio_max))
        except ValueError:
            pass
            
    if busqueda:
        busqueda_fuzzy = f"%{busqueda.strip()}%"
        query = query.filter(
            (Alojamiento.titulo.ilike(busqueda_fuzzy)) |
            (Alojamiento.ubicacion.ilike(busqueda_fuzzy)) |
            (Alojamiento.provincia.ilike(busqueda_fuzzy)) |
            (Alojamiento.descripcion.ilike(busqueda_fuzzy))
        )
        
    alojamientos = query.order_by(Alojamiento.destacado.desc(), Alojamiento.calificacion.desc()).all()
    return jsonify([aloj.to_dict() for aloj in alojamientos]), 200


@alojamientos_bp.route("/<string:id>", methods=["GET"])
def obtener_alojamiento(id):
    alojamiento = Alojamiento.query.get(id)
    if not alojamiento:
        return jsonify({"error": "Alojamiento no encontrado."}), 404
    return jsonify(alojamiento.to_dict()), 200


@alojamientos_bp.route("", methods=["POST"])
@role_required("comercial", "general")
def crear_alojamiento():
    """Permite a administradores dar de alta un nuevo alojamiento completo."""
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos."}), 400
        
    titulo = datos.get("title") or datos.get("titulo")
    ubicacion = datos.get("location") or datos.get("ubicacion")
    provincia = datos.get("province") or datos.get("provincia")
    precio = datos.get("price") or datos.get("precio")
    tipo = datos.get("type") or datos.get("tipo")
    descripcion = datos.get("description") or datos.get("descripcion")
    
    if not titulo or not ubicacion or not provincia or not precio or not tipo or not descripcion:
        return jsonify({"error": "Faltan campos obligatorios: titulo, ubicacion, provincia, precio, tipo y descripcion."}), 400
        
    try:
        precio_int = int(precio)
        if precio_int <= 0:
            return jsonify({"error": "El precio debe ser un numero positivo."}), 400
    except ValueError:
        return jsonify({"error": "El precio debe ser un valor numerico valido."}), 400
        
    # Generar ID unico
    id_base = datos.get("id") or f"{generar_slug(provincia)}-{generar_slug(titulo)}"
    id_final = id_base
    counter = 1
    while Alojamiento.query.get(id_final):
        id_final = f"{id_base}-{counter}"
        counter += 1
        
    imagenes = datos.get("images") or datos.get("imagenes") or []
    if not isinstance(imagenes, list) or len(imagenes) == 0:
        imagenes = ["https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=800&auto=format&fit=crop"]
        
    experience_label = datos.get("experienceLabel") or datos.get("experience_label") or "Experiencia Exclusiva"
    
    nuevo_alojamiento = Alojamiento(
        id=id_final,
        titulo=titulo,
        ubicacion=ubicacion,
        provincia=provincia,
        precio=precio_int,
        calificacion=float(datos.get("rating", 5.0)),
        reviews_count=int(datos.get("reviewsCount", 0)),
        tipo=tipo,
        experience_label=experience_label,
        descripcion=descripcion,
        destacado=bool(datos.get("featured", False)),
        activo=bool(datos.get("active", True)),
        descuento=int(datos.get("discount", 0))
    )
    nuevo_alojamiento.imagenes = imagenes
    
    # Agregar actividades
    actividades_list = datos.get("activities") or datos.get("actividades") or []
    for act_desc in actividades_list:
        if isinstance(act_desc, str) and act_desc.strip():
            nuevo_alojamiento.actividades.append(Actividad(descripcion=act_desc.strip()))
            
    # Agregar servicios
    servicios_list = datos.get("amenities") or datos.get("servicios") or []
    for srv_nom in servicios_list:
        if isinstance(srv_nom, str) and srv_nom.strip():
            nuevo_alojamiento.servicios.append(Servicio(nombre=srv_nom.strip()))
            
    try:
        db.session.add(nuevo_alojamiento)
        db.session.commit()
        return jsonify({
            "mensaje": "Alojamiento creado exitosamente.",
            "alojamiento": nuevo_alojamiento.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al guardar alojamiento: {str(e)}"}), 500


@alojamientos_bp.route("/<string:id>", methods=["PUT"])
@role_required("comercial", "general")
def editar_alojamiento(id):
    """Permite editar campos principales de un alojamiento."""
    alojamiento = Alojamiento.query.get(id)
    if not alojamiento:
        return jsonify({"error": "Alojamiento no encontrado."}), 404
        
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos para actualizar."}), 400
        
    if "title" in datos or "titulo" in datos:
        alojamiento.titulo = datos.get("title") or datos.get("titulo")
    if "location" in datos or "ubicacion" in datos:
        alojamiento.ubicacion = datos.get("location") or datos.get("ubicacion")
    if "province" in datos or "provincia" in datos:
        alojamiento.provincia = datos.get("province") or datos.get("provincia")
    if "price" in datos or "precio" in datos:
        alojamiento.precio = int(datos.get("price") or datos.get("precio"))
    if "type" in datos or "tipo" in datos:
        alojamiento.tipo = datos.get("type") or datos.get("tipo")
    if "description" in datos or "descripcion" in datos:
        alojamiento.descripcion = datos.get("description") or datos.get("descripcion")
    if "images" in datos or "imagenes" in datos:
        alojamiento.imagenes = datos.get("images") or datos.get("imagenes")
    if "featured" in datos or "destacado" in datos:
        alojamiento.destacado = bool(datos.get("featured") if "featured" in datos else datos.get("destacado"))
        
    try:
        db.session.commit()
        return jsonify({
            "mensaje": "Alojamiento actualizado con exito.",
            "alojamiento": alojamiento.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar alojamiento: {str(e)}"}), 500


@alojamientos_bp.route("/<string:id>", methods=["DELETE"])
@role_required("comercial", "general")
def eliminar_alojamiento(id):
    """Baja de alojamiento."""
    alojamiento = Alojamiento.query.get(id)
    if not alojamiento:
        return jsonify({"error": "Alojamiento no encontrado."}), 404
        
    try:
        db.session.delete(alojamiento)
        db.session.commit()
        return jsonify({"mensaje": f"Alojamiento '{alojamiento.titulo}' eliminado correctamente."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"No se pudo eliminar el alojamiento: {str(e)}"}), 500


@alojamientos_bp.route("/<string:id>/visibilidad", methods=["PUT"])
@role_required("comercial", "general")
def cambiar_visibilidad(id):
    alojamiento = Alojamiento.query.get(id)
    if not alojamiento:
        return jsonify({"error": "Alojamiento no encontrado."}), 404
        
    datos = request.get_json()
    activo = datos.get("activo") if datos else None
    if activo is None:
        return jsonify({"error": "Falta el campo 'activo' (booleano)."}), 400
        
    alojamiento.activo = bool(activo)
    try:
        db.session.commit()
        return jsonify({"mensaje": "Visibilidad actualizada con exito.", "alojamiento": alojamiento.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@alojamientos_bp.route("/<string:id>/promocion", methods=["PUT"])
@role_required("comercial", "general")
def cambiar_promocion(id):
    alojamiento = Alojamiento.query.get(id)
    if not alojamiento:
        return jsonify({"error": "Alojamiento no encontrado."}), 404
        
    datos = request.get_json()
    descuento = datos.get("descuento") if datos else None
    if descuento is None:
        return jsonify({"error": "Falta el campo 'descuento'."}), 400
        
    if descuento not in [0, 10, 25, 50]:
        return jsonify({"error": "Descuento invalido. Valores permitidos: 0, 10, 25, 50."}), 400
        
    alojamiento.descuento = int(descuento)
    try:
        db.session.commit()
        return jsonify({"mensaje": "Promocion actualizada con exito.", "alojamiento": alojamiento.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from models import db, Usuario, Reserva
from utils.decorators import role_required
from services.stats_service import calculate_dashboard_statistics

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/usuarios", methods=["GET"])
@role_required("general")
def listar_usuarios():
    """Lista todos los usuarios registrados para el administrador general."""
    usuarios = Usuario.query.order_by(Usuario.fecha_creacion.desc()).all()
    return jsonify([u.to_dict() for u in usuarios]), 200


@admin_bp.route("/usuarios/<int:id>/rol", methods=["PUT"])
@role_required("general")
def cambiar_rol_usuario(id):
    """Actualiza el rol de un usuario."""
    usuario_solicitante_id = int(get_jwt_identity())
    
    datos = request.get_json()
    nuevo_rol = datos.get("rol") if datos else None
    
    if not nuevo_rol or nuevo_rol not in ["cliente", "comercial", "general"]:
        return jsonify({"error": "Rol invalido. Opciones permitidas: 'cliente', 'comercial', 'general'."}), 400
        
    usuario_destino = Usuario.query.get(id)
    if not usuario_destino:
        return jsonify({"error": "Usuario no encontrado."}), 404
        
    # Evitar que el administrador general se degrade a si mismo accidentalmente si es el unico
    if usuario_destino.id == usuario_solicitante_id and nuevo_rol != "general":
        admins_totales = Usuario.query.filter_by(rol="general").count()
        if admins_totales <= 1:
            return jsonify({"error": "No puedes quitarte el rol de Administrador General siendo el unico en el sistema."}), 400
            
    usuario_destino.rol = nuevo_rol
    try:
        db.session.commit()
        return jsonify({
            "mensaje": f"Rol de {usuario_destino.nombre} actualizado a '{nuevo_rol}'.",
            "usuario": usuario_destino.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar el rol: {str(e)}"}), 500


@admin_bp.route("/estadisticas", methods=["GET"])
@role_required("general")
def obtener_estadisticas():
    """Retorna metricas financieras y operativas dinamicamente calculadas."""
    stats = calculate_dashboard_statistics()
    return jsonify(stats), 200


@admin_bp.route("/reservas", methods=["GET"])
@role_required("comercial", "general")
def listar_todas_las_reservas():
    """
    Permite a los administradores comerciales y generales consultar
    todas las reservas del sistema con filtros opcionales.
    """
    estado = request.args.get("estado")
    alojamiento_id = request.args.get("alojamiento_id")
    
    query = Reserva.query
    if estado and estado != "all":
        query = query.filter_by(estado=estado)
    if alojamiento_id and alojamiento_id != "all":
        query = query.filter_by(alojamiento_id=alojamiento_id)
        
    reservas = query.order_by(Reserva.fecha_creacion.desc()).all()
    return jsonify([r.to_dict() for r in reservas]), 200


@admin_bp.route("/reservas/<int:id>/estado", methods=["PUT"])
@role_required("comercial", "general")
def cambiar_estado_reserva(id):
    """
    Permite aprobar (confirmar) o cancelar una reserva solicitada.
    """
    reserva = Reserva.query.get(id)
    if not reserva:
        return jsonify({"error": "Reserva no encontrada."}), 404
        
    datos = request.get_json()
    nuevo_estado = datos.get("estado") if datos else None
    
    if not nuevo_estado or nuevo_estado not in ["pending", "confirmed", "cancelled"]:
        return jsonify({"error": "Estado invalido. Permitidos: 'pending', 'confirmed', 'cancelled'."}), 400
        
    reserva.estado = nuevo_estado
    try:
        db.session.commit()
        return jsonify({
            "mensaje": f"Reserva #{reserva.id} actualizada al estado '{nuevo_estado}'.",
            "reserva": reserva.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al actualizar estado: {str(e)}"}), 500

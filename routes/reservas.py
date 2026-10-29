from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Reserva, Alojamiento, Usuario
from services.booking_service import parse_and_validate_dates, check_availability, calculate_total_price

reservas_bp = Blueprint("reservas", __name__)

@reservas_bp.route("", methods=["POST"])
@jwt_required()
def crear_reserva():
    usuario_id = get_jwt_identity()
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos en la peticion."}), 400
        
    alojamiento_id = datos.get("alojamiento_id")
    check_in_str = datos.get("check_in")
    check_out_str = datos.get("check_out")
    huespedes = datos.get("huespedes", 1)
    notes = datos.get("notes", "")
    
    if not alojamiento_id or not check_in_str or not check_out_str:
        return jsonify({"error": "Falta informacion obligatoria: alojamiento_id, check_in o check_out."}), 400
        
    alojamiento = Alojamiento.query.get(alojamiento_id)
    if not alojamiento:
        return jsonify({"error": "El alojamiento seleccionado no existe."}), 404
        
    if not alojamiento.activo:
        return jsonify({"error": "El alojamiento no se encuentra activo para reservas en este momento."}), 400
        
    # 1. Validar formato y coherencia temporal de fechas
    check_in, check_out, error_fecha = parse_and_validate_dates(check_in_str, check_out_str)
    if error_fecha:
        return jsonify({"error": error_fecha}), 400
        
    # 2. Control de solapamiento / Overbooking
    disponible, conflicto = check_availability(alojamiento_id, check_in, check_out)
    if not disponible:
        return jsonify({
            "error": "El alojamiento ya cuenta con una reserva activa para el rango de fechas seleccionado.",
            "fechas_conflicto": {
                "check_in": conflicto.check_in.isoformat(),
                "check_out": conflicto.check_out.isoformat()
            }
        }), 409
        
    # 3. Calcular precio total dinamico (con descuentos y tasas de servicio)
    precio_total = calculate_total_price(alojamiento, check_in, check_out)
    
    try:
        huespedes_int = max(1, int(huespedes))
    except (ValueError, TypeError):
        huespedes_int = 1
        
    nueva_reserva = Reserva(
        usuario_id=int(usuario_id),
        alojamiento_id=alojamiento_id,
        check_in=check_in,
        check_out=check_out,
        huespedes=huespedes_int,
        notes=notes.strip() if isinstance(notes, str) else "",
        precio_total=precio_total,
        estado="pending"
    )
    
    try:
        db.session.add(nueva_reserva)
        db.session.commit()
        return jsonify({
            "mensaje": "Reserva solicitada con exito.",
            "reserva": nueva_reserva.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al procesar la reserva en base de datos: {str(e)}"}), 500


@reservas_bp.route("", methods=["GET"])
@jwt_required()
def listar_mis_reservas():
    usuario_id = get_jwt_identity()
    reservas = Reserva.query.filter_by(usuario_id=int(usuario_id)).order_by(Reserva.fecha_creacion.desc()).all()
    return jsonify([res.to_dict() for res in reservas]), 200


@reservas_bp.route("/<int:id>/cancelar", methods=["PUT"])
@jwt_required()
def cancelar_reserva(id):
    """Permite al cliente o a un administrador cancelar una reserva."""
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(int(usuario_id))
    
    reserva = Reserva.query.get(id)
    if not reserva:
        return jsonify({"error": "Reserva no encontrada."}), 404
        
    # Verificar propiedad de la reserva o rol administrador
    es_propietario = (reserva.usuario_id == int(usuario_id))
    es_admin = (usuario and usuario.rol in ["comercial", "general"])
    
    if not (es_propietario or es_admin):
        return jsonify({"error": "No tienes autorizacion para cancelar esta reserva."}), 403
        
    if reserva.estado == "cancelled":
        return jsonify({"mensaje": "La reserva ya se encontraba cancelada.", "reserva": reserva.to_dict()}), 200
        
    reserva.estado = "cancelled"
    try:
        db.session.commit()
        return jsonify({
            "mensaje": "Reserva cancelada exitosamente.",
            "reserva": reserva.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al cancelar la reserva: {str(e)}"}), 500

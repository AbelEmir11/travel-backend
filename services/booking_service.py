from datetime import datetime, date
from models import Reserva, Alojamiento

SERVICE_FEE_USD = 40

def parse_and_validate_dates(check_in_str, check_out_str):
    """
    Parsea cadenas YYYY-MM-DD y valida la coherencia temporal.
    Retorna (check_in_date, check_out_date, error_msg).
    """
    if not check_in_str or not check_out_str:
        return None, None, "Se requieren ambas fechas (check-in y check-out)."
        
    try:
        check_in = datetime.strptime(str(check_in_str).strip(), "%Y-%m-%d").date()
        check_out = datetime.strptime(str(check_out_str).strip(), "%Y-%m-%d").date()
    except ValueError:
        return None, None, "Formato de fecha invalido. Utilice el formato AAAA-MM-DD."
        
    hoy = date.today()
    if check_in < hoy:
        return None, None, "La fecha de check-in no puede ser anterior al dia de hoy."
        
    if check_in >= check_out:
        return None, None, "La fecha de salida (check-out) debe ser posterior a la fecha de entrada (check-in)."
        
    return check_in, check_out, None


def check_availability(alojamiento_id, check_in, check_out, exclude_reserva_id=None):
    """
    Verifica si existe solapamiento con reservas activas (pending o confirmed).
    Formula de solapamiento de intervalos [A_in, A_out] y [B_in, B_out]:
      (A_in < B_out) and (A_out > B_in)
    Retorna (disponible: bool, reserva_en_conflicto: Reserva|None).
    """
    query = Reserva.query.filter(
        Reserva.alojamiento_id == alojamiento_id,
        Reserva.estado.in_(["pending", "confirmed"]),
        Reserva.check_in < check_out,
        Reserva.check_out > check_in
    )
    
    if exclude_reserva_id:
        query = query.filter(Reserva.id != exclude_reserva_id)
        
    conflicto = query.first()
    if conflicto:
        return False, conflicto
    return True, None


def calculate_total_price(alojamiento, check_in, check_out):
    """
    Calcula el costo total considerando noches, descuento activo y tarifa de servicio fija.
    """
    noches = max(1, (check_out - check_in).days)
    descuento = getattr(alojamiento, "descuento", 0) or 0
    precio_base = alojamiento.precio
    
    if descuento > 0:
        precio_noche = round(precio_base * (1 - (descuento / 100)))
    else:
        precio_noche = precio_base
        
    precio_total = (precio_noche * noches) + SERVICE_FEE_USD
    return int(precio_total)

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
import re
from models import Usuario

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def is_valid_email(email):
    """Valida formato de correo electronico."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def get_current_user():
    """Obtiene la instancia del modelo Usuario segun la identidad JWT actual."""
    identidad = get_jwt_identity()
    if not identidad:
        return None
    try:
        return Usuario.query.get(int(identidad))
    except (ValueError, TypeError):
        return None

def role_required(*allowed_roles):
    """
    Decorador para proteger rutas segun el rol del usuario autenticado.
    Ejemplo: @role_required('comercial', 'general')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            usuario = get_current_user()
            if not usuario:
                return jsonify({"error": "Usuario no encontrado o sesion invalida."}), 404
            
            if usuario.rol not in allowed_roles:
                return jsonify({
                    "error": "Acceso denegado.",
                    "mensaje": f"Se requiere uno de los siguientes roles: {', '.join(allowed_roles)}. Tu rol actual es: '{usuario.rol}'."
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

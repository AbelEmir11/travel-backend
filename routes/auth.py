from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario
from utils.decorators import is_valid_email

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/registro", methods=["POST"])
def registro():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos en la peticion."}), 400
        
    nombre = datos.get("nombre", "").strip()
    email = datos.get("email", "").strip().lower()
    password = datos.get("password", "")
    
    if not nombre or not email or not password:
        return jsonify({"error": "Por favor completa todos los campos obligatorios (nombre, email, password)."}), 400
        
    if not is_valid_email(email):
        return jsonify({"error": "El formato del correo electronico no es valido."}), 400
        
    if len(password) < 6:
        return jsonify({"error": "La contrasena debe tener al menos 6 caracteres."}), 400
        
    # Verificar si el usuario ya existe
    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "El correo electronico ya esta registrado."}), 400
        
    # Crear usuario
    password_hash = generate_password_hash(password)
    nuevo_usuario = Usuario(nombre=nombre, email=email, password_hash=password_hash, rol="cliente")
    
    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        token_acceso = create_access_token(identity=str(nuevo_usuario.id))
        return jsonify({
            "mensaje": "Usuario registrado con exito.",
            "token": token_acceso,
            "usuario": nuevo_usuario.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno al registrar usuario: {str(e)}"}), 500


@auth_bp.route("/ingreso", methods=["POST"])
def ingreso():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos en la peticion."}), 400
        
    email = datos.get("email", "").strip().lower()
    password = datos.get("password", "")
    
    if not email or not password:
        return jsonify({"error": "Por favor ingresa tanto el email como la contrasena."}), 400
        
    usuario = Usuario.query.filter_by(email=email).first()
    
    if not usuario or not check_password_hash(usuario.password_hash, password):
        return jsonify({"error": "Credenciales incorrectas. Verifica tu email y contrasena."}), 401
        
    token_acceso = create_access_token(identity=str(usuario.id))
    return jsonify({
        "mensaje": "Ingreso exitoso.",
        "token": token_acceso,
        "usuario": usuario.to_dict()
    }), 200


@auth_bp.route("/perfil", methods=["GET"])
@jwt_required()
def obtener_perfil():
    usuario_id = get_jwt_identity()
    try:
        usuario = Usuario.query.get(int(usuario_id))
    except (ValueError, TypeError):
        return jsonify({"error": "Identificador de usuario invalido."}), 400
        
    if not usuario:
        return jsonify({"error": "Usuario no encontrado."}), 404
        
    return jsonify(usuario.to_dict()), 200

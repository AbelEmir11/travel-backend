from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from datetime import timedelta
from config import Config
from models import db
from routes import register_blueprints

jwt = JWTManager()
migrate = Migrate()

def create_app(config_class=Config):
    """
    Application Factory para inicializar Flask, extensiones y Blueprints.
    Permite instanciar la aplicacion tanto en ejecucion como en tests.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Expiracion extendida de tokens JWT
    app.config.setdefault("JWT_ACCESS_TOKEN_EXPIRES", timedelta(days=30))
    
    # Extensiones
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    
    # Registro modular de Blueprints
    register_blueprints(app)

    # Ruta raiz de bienvenida informativa
    @app.route("/", methods=["GET"])
    @app.route("/api", methods=["GET"])
    def index():
        return jsonify({
            "servicio": "TRAVEL API REST",
            "version": "2.0.0",
            "estado": "online",
            "documentacion_endpoints": {
                "alojamientos": "/api/alojamientos",
                "autenticacion": "/api/autenticacion",
                "reservas": "/api/reservas",
                "admin": "/api/admin"
            }
        }), 200
    
    # Manejadores de errores globales estandarizados
    @app.errorhandler(404)
    def recurso_no_encontrado(error):
        return jsonify({"error": "Recurso no encontrado.", "codigo": 404}), 404

    @app.errorhandler(500)
    def error_interno_servidor(error):
        return jsonify({"error": "Error interno del servidor.", "codigo": 500}), 500

    @jwt.unauthorized_loader
    def token_faltante_callback(reason):
        return jsonify({"error": "Falta token de autorizacion (Bearer token).", "detalle": reason}), 401

    @jwt.invalid_token_loader
    def token_invalido_callback(reason):
        return jsonify({"error": "Token de autenticacion invalido o expirado.", "detalle": reason}), 401

    # Crear tablas si no existen (en modo desarrollo)
    with app.app_context():
        db.create_all()
        
    return app

# Instancia exportada por defecto para ejecucion directa con run.py o gunicorn
app = create_app()

if __name__ == "__main__":
    app.run(port=5000, debug=True)

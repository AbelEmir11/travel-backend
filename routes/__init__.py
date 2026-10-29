from .auth import auth_bp
from .alojamientos import alojamientos_bp
from .reservas import reservas_bp
from .admin import admin_bp

def register_blueprints(app):
    """Registra todos los Blueprints con sus prefijos correspondientes."""
    app.register_blueprint(auth_bp, url_prefix="/api/autenticacion")
    app.register_blueprint(alojamientos_bp, url_prefix="/api/alojamientos")
    app.register_blueprint(reservas_bp, url_prefix="/api/reservas")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

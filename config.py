import os
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'travel-session-fallback-secret-2026')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'travel-jwt-fallback-secret-2026')
    
    db_url = os.environ.get('DATABASE_URL')
    
    # Validar si el usuario completó la contraseña de MySQL
    if not db_url or "TU_CONTRASENA_MYSQL" in db_url:
        print("\n" + "="*70)
        print("[AVISO] No se configuro una contrasena de MySQL en '.env'.")
        print("[INFO] Se utilizara una base de datos local SQLite ('travel.db') de respaldo.")
        print("[INFO] Para usar tu servidor MySQL Workbench:")
        print("   1. Crea la base de datos 'travel_db' en tu Workbench.")
        print("   2. Actualiza tu contrasena en el archivo '.env' del servidor backend.")
        print("="*70 + "\n")
        db_url = "sqlite:///travel.db"
        
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

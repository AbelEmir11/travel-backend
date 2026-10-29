import os
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

def get_database_uri():
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url or "TU_CONTRASENA_MYSQL" in db_url:
        return "sqlite:///travel.db"
        
    # Compatibilidad con Supabase / Heroku / Render PostgreSQL (cambiar postgres:// por postgresql://)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    if db_url.startswith("postgresql"):
        return db_url

    if db_url.startswith("mysql"):
        try:
            import pymysql
            from urllib.parse import urlparse
            parsed = urlparse(db_url)
            conn = pymysql.connect(
                host=parsed.hostname or 'localhost',
                user=parsed.username or 'root',
                password=parsed.password or '',
                port=parsed.port or 3306,
                connect_timeout=1
            )
            conn.close()
            return db_url
        except Exception:
            print("\n" + "="*70)
            print("[INFO] Servidor MySQL no disponible localmente en el puerto 3306.")
            print("[INFO] Utilizando base de datos SQLite ('travel.db') de respaldo seguro.")
            print("="*70 + "\n")
            return "sqlite:///travel.db"
            
    return db_url


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'travel-session-fallback-secret-2026')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'travel-jwt-fallback-secret-2026')
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig:
    TESTING = True
    SECRET_KEY = "test-secret-key-super-secure-32bytes-min"
    JWT_SECRET_KEY = "test-jwt-secret-key-super-secure-32bytes-min"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

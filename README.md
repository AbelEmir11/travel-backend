# TRAVEL - API Backend (Flask & MySQL)

Este es el backend de la aplicación **TRAVEL**, desarrollado en Python utilizando el micro-framework **Flask** y el ORM **SQLAlchemy** para la persistencia de datos en una base de datos relacional MySQL (o SQLite como fallback). 

La API está diseñada siguiendo principios RESTful y gestiona la autenticación de usuarios mediante JSON Web Tokens (JWT), el catálogo de alojamientos turísticos y el procesamiento de reservas.

---

## 🚀 Tecnologías Utilizadas

*   **Python 3.x**
*   **Flask** (Servidor web y ruteo)
*   **Flask-SQLAlchemy** (Mapeo objeto-relacional ORM)
*   **Flask-JWT-Extended** (Autenticación y protección de rutas con tokens)
*   **Flask-CORS** (Habilitación de peticiones cruzadas con el frontend)
*   **PyMySQL & Cryptography** (Conectores nativos para base de datos MySQL)
*   **Werkzeug** (Hasheo seguro de contraseñas mediante Scrypt)

---

## 📋 Arquitectura de Base de Datos (Modelos)

El sistema cuenta con cuatro modelos principales definidos en `models.py`:
1.  **Usuario (`usuario`):** Almacena credenciales de acceso, fecha de creación y el `rol` correspondiente (`"cliente"`, `"comercial"`, `"general"`).
2.  **Alojamiento (`alojamiento`):** Contiene título, descripción, precio base, calificación, tipo de experiencia, descuento promocional, y estados lógicos de visibilidad (`activo`).
3.  **Reserva (`reserva`):** Registra el check-in, check-out, cantidad de huéspedes, precio final calculado con descuento, notas especiales y estado de aprobación (`"pending"`, `"confirmed"`, `"cancelled"`).
4.  **Actividades & Servicios:** Tablas secundarias que proveen el listado detallado de amenidades para cada hospedaje de lujo.

---

## ⚙️ Requisitos e Instalación

### 1. Variables de Entorno (`.env`)
Creá un archivo `.env` en la raíz del directorio `/travel-backend` con las siguientes configuraciones de conexión:
```env
FLASK_APP=app.py
FLASK_ENV=development
JWT_SECRET_KEY=clave_secreta_super_segura
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost/travel_db
```
*(Si no se define la URL de MySQL o no se puede conectar, la aplicación creará automáticamente una base de datos SQLite local llamada `travel.db` en la carpeta `instance`).*

### 2. Instalación de Dependencias
Con tu terminal de preferencia en la carpeta del backend, ejecutá:

**En Bash (Git Bash o WSL):**
```bash
# Activar entorno virtual
source venv/Scripts/activate

# Instalar los paquetes
pip install flask flask-sqlalchemy flask-cors flask-jwt-extended pymysql cryptography
```

**En PowerShell / CMD:**
```powershell
# Activar entorno virtual
.\venv\Scripts\activate

# Instalar los paquetes
pip install flask flask-sqlalchemy flask-cors flask-jwt-extended pymysql cryptography
```

### 3. Cargar Base de Datos y Semillas
Para crear las tablas desde cero e inyectar los datos semilla (hoteles representativos de Argentina y usuarios de prueba), ejecutá:
```bash
python semilla.py
```

---

## 👥 Cuentas de Prueba Preconfiguradas

El script `semilla.py` crea los siguientes usuarios con roles diferenciados para validar la seguridad y los paneles:

| Rol | Correo Electrónico | Contraseña |
| :--- | :--- | :--- |
| **Cliente** | `cliente@travel.com` | `cliente123` |
| **Administrador Comercial** | `comercial@travel.com` | `comercial123` |
| **Administrador General** | `general@travel.com` | `general123` |

---

## 📡 Endpoints de la API (Resumen)

Todas las rutas están definidas bajo el prefijo `/api`:

### Autenticación
*   `POST /autenticacion/registro` -> Registro de nuevos clientes.
*   `POST /autenticacion/ingreso` -> Login y retorno de JWT + datos de usuario (incluyendo el rol).
*   `GET /autenticacion/perfil` -> Retorna el perfil del usuario autenticado (Protegido por JWT).

### Alojamientos
*   `GET /alojamientos` -> Listado general. Filtra inactivos para clientes. Retorna catálogo completo para administradores.
*   `GET /alojamientos/<id>` -> Detalle de un hospedaje específico.
*   `PUT /alojamientos/<id>/visibilidad` -> Habilitar o dar de baja temporalmente la visualización (Comercial/General).
*   `PUT /alojamientos/<id>/promocion` -> Asignar descuento promocional (0, 10, 25, 50%) (Comercial/General).

### Reservas y Administración
*   `POST /reservas` -> Crea una solicitud de reserva con validación de fechas (Cliente).
*   `GET /reservas` -> Historial de reservas asociadas al cliente logueado (Cliente).
*   `GET /admin/usuarios` -> Listar personal del sistema (General).
*   `PUT /admin/usuarios/<id>/rol` -> Cambiar rol o permisos de un usuario (General).
*   `GET /admin/estadisticas` -> Métricas comerciales, facturación mensual 2026 y reservas por provincia (General).

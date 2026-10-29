# TRAVEL - API Backend Modular (Flask, Blueprints & MySQL / SQLite)

Backend de la plataforma **TRAVEL**, desarrollado en Python utilizando **Flask**, arquitectura modular mediante **Blueprints**, **SQLAlchemy** como ORM, autenticación por **JWT** y base de datos relacional (MySQL con fallback transparente a SQLite).

---

## 🏛️ Arquitectura del Sistema

El backend ha sido refactorizado bajo una estructura modular por capas:

```
travel-backend/
├── routes/                  # Blueprints de endpoints REST
│   ├── auth.py              # /api/autenticacion (registro, ingreso, perfil)
│   ├── alojamientos.py      # /api/alojamientos (CRUD completo, promociones, visibilidad)
│   ├── reservas.py          # /api/reservas (overbooking check, mis reservas, cancelaciones)
│   └── admin.py             # /api/admin (metricas dinamicas, gestion de roles y reservas)
├── services/                # Logica de negocio desacoplada
│   ├── booking_service.py   # Validacion temporal, deteccion de solapamiento y calculo de tarifas
│   └── stats_service.py     # Calculo dinamico de KPIs financieros sin datos hardcodeados
├── utils/                   # Helpers y decoradores
│   └── decorators.py        # Control de acceso basado en roles (@role_required)
├── tests/                   # Suite de pruebas automatizadas
│   ├── test_auth.py         # Tests de registro, login, contrasenas y tokens
│   └── test_reservas.py     # Tests de creacion, cancelacion y deteccion de overbooking (409)
├── app.py                   # Application Factory (create_app)
├── config.py                # Configuraciones de entorno (Dev, Prod, Test)
├── models.py                # Modelos relacionales SQLAlchemy
├── run.py                   # Servidor de desarrollo
└── semilla.py               # Script de poblacion inicial
```

---

## 🚀 Logica de Negocio Destacada

1. **Prevencion de Overbooking / Solapamiento de Fechas:**
   * La creacion de reservas verifica si existe una reserva confirmada o pendiente para el mismo alojamiento en el rango `[check_in, check_out]`.
   * Si hay conflicto, responde con código HTTP `409 Conflict`.
2. **Calculo Dinamico de Precios:**
   * Aplica descuentos vigentes del alojamiento (`10%`, `25%`, `50%`) por noche + tasa fija de servicio.
3. **Control de Acceso por Roles:**
   * Roles: `cliente`, `comercial`, `general`.
   * Proteccion de endpoints mediante el decorador `@role_required`.
4. **Metricas Financieras Reales:**
   * El panel de administracion general calcula ingresos mes a mes dinamicamente segun el ano actual.

---

## ⚙️ Instalacion y Ejecucion

### 1. Activar Entorno Virtual
```powershell
cd travel-backend
.\venv\Scripts\Activate.ps1
```

### 2. Instalar Dependencias
```powershell
pip install -r requirements.txt
```

### 3. Poblar la Base de Datos con Semilla
```powershell
python semilla.py
```

### 4. Ejecutar el Servidor
```powershell
python run.py
```
Servidor disponible en: `http://localhost:5000/api`

---

## 🧪 Ejecutar la Suite de Pruebas Automatizadas

Para correr los tests con SQLite en memoria (sin afectar tu base de datos de desarrollo):

```powershell
python -m unittest discover tests
```
O usando pytest:
```powershell
pytest
```

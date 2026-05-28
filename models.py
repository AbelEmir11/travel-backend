from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    reservas = db.relationship('Reserva', backref='usuario', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.nombre,
            "email": self.email,
            "fecha_creacion": self.fecha_creacion.isoformat()
        }


class Alojamiento(db.Model):
    __tablename__ = 'alojamiento'
    
    id = db.Column(db.String(50), primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    provincia = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    calificacion = db.Column(db.Float, default=5.0)
    reviews_count = db.Column(db.Integer, default=0)
    imagenes_json = db.Column(db.Text, nullable=False)  # Guarda la lista en formato JSON
    tipo = db.Column(db.String(50), nullable=False)  # estadia, viaje, all_inclusive
    experience_label = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    destacado = db.Column(db.Boolean, default=False)
    
    actividades = db.relationship('Actividad', backref='alojamiento', lazy=True, cascade="all, delete-orphan")
    servicios = db.relationship('Servicio', backref='alojamiento', lazy=True, cascade="all, delete-orphan")
    reservas = db.relationship('Reserva', backref='alojamiento', lazy=True, cascade="all, delete-orphan")

    @property
    def imagenes(self):
        try:
            return json.loads(self.imagenes_json)
        except:
            return []

    @imagenes.setter
    def imagenes(self, value):
        self.imagenes_json = json.dumps(value)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.titulo,
            "location": self.ubicacion,
            "province": self.provincia,
            "price": self.precio,
            "rating": self.calificacion,
            "reviewsCount": self.reviews_count,
            "images": self.imagenes,
            "type": self.tipo,
            "experienceLabel": self.experience_label,
            "description": self.descripcion,
            "featured": self.destacado,
            "activities": [act.descripcion for act in self.actividades],
            "amenities": [srv.nombre for srv in self.servicios]
        }


class Actividad(db.Model):
    __tablename__ = 'actividad'
    
    id = db.Column(db.Integer, primary_key=True)
    alojamiento_id = db.Column(db.String(50), db.ForeignKey('alojamiento.id', ondelete='CASCADE'), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)


class Servicio(db.Model):
    __tablename__ = 'servicio'
    
    id = db.Column(db.Integer, primary_key=True)
    alojamiento_id = db.Column(db.String(50), db.ForeignKey('alojamiento.id', ondelete='CASCADE'), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)


class Reserva(db.Model):
    __tablename__ = 'reserva'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    alojamiento_id = db.Column(db.String(50), db.ForeignKey('alojamiento.id', ondelete='CASCADE'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    huespedes = db.Column(db.Integer, default=1)
    notes = db.Column(db.Text, nullable=True)
    precio_total = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(20), default="pending")  # pending, confirmed, cancelled
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "alojamiento_id": self.alojamiento_id,
            "alojamiento_titulo": self.alojamiento.titulo if self.alojamiento else "",
            "alojamiento_ubicacion": self.alojamiento.ubicacion if self.alojamiento else "",
            "alojamiento_provincia": self.alojamiento.provincia if self.alojamiento else "",
            "alojamiento_imagen": self.alojamiento.imagenes[0] if self.alojamiento and self.alojamiento.imagenes else "",
            "check_in": self.check_in.isoformat(),
            "check_out": self.check_out.isoformat(),
            "huespedes": self.huespedes,
            "notes": self.notes,
            "precio_total": self.precio_total,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion.isoformat()
        }

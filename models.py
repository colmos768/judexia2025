from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    rut = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(200))
    fecha_nacimiento = db.Column(db.Date)

    causas = db.relationship('Causa', backref='cliente', lazy=True)
    pagos = db.relationship('Pago', backref='cliente', lazy=True)

class Causa(db.Model):
    __tablename__ = 'causas'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    rol = db.Column(db.String(20))
    tribunal = db.Column(db.String(100))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)

class Pago(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.String(20))  # o db.Date si prefieres
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)

class FormatoLegal(db.Model):
    __tablename__ = 'formatos_legales'
    id = db.Column(db.Integer, primary_key=True)
    nombre_original = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.Column(db.String(100))  # puedes asociarlo a un modelo de usuarios si más adelante lo creas

    causa_id = db.Column(db.Integer, db.ForeignKey('causas.id'))
    causa = db.relationship('Causa', backref='formatos')

    version = db.Column(db.Integer, default=1)
    observaciones = db.Column(db.String(255))

class Honorario(Base):
    __tablename__ = 'honorarios'
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    causa_id = Column(Integer, ForeignKey('causas.id'), nullable=True)  # opcional
    descripcion = Column(String(255))
    monto_total = Column(Float)
    fecha_emision = Column(Date)
    en_cuotas = Column(Boolean, default=False)
    numero_cuotas = Column(Integer, default=1)
    estado = Column(String(50), default="pendiente")  # pendiente / pagado / moroso

    cliente = relationship("Cliente", back_populates="honorarios")
    causa = relationship("Causa", back_populates="honorarios")
    pagos = relationship("PagoCuota", back_populates="honorario", cascade="all, delete")

class PagoCuota(Base):
    __tablename__ = 'pagos_cuotas'
    id = Column(Integer, primary_key=True)
    honorario_id = Column(Integer, ForeignKey('honorarios.id'))
    numero_cuota = Column(Integer)
    monto_pagado = Column(Float)
    fecha_pago = Column(Date)
    vencimiento = Column(Date)
    estado = Column(String(20), default="pendiente")  # pendiente / pagado / vencida

    honorario = relationship("Honorario", back_populates="pagos")

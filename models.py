from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

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
    honorarios = db.relationship('Honorario', backref='cliente', lazy=True)


class Causa(db.Model):
    __tablename__ = 'causas'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))
    rol = db.Column(db.String(20))
    tribunal = db.Column(db.String(100))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)

    honorarios = db.relationship('Honorario', backref='causa', lazy=True)


class Pago(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.String(20))  # puede ser db.Date si prefieres
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)


class FormatoLegal(db.Model):
    __tablename__ = 'formatos_legales'
    id = db.Column(db.Integer, primary_key=True)
    nombre_original = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.Column(db.String(100))  # Puedes asociarlo a un modelo de usuarios si lo implementas

    causa_id = db.Column(db.Integer, db.ForeignKey('causas.id'))
    causa = db.relationship('Causa', backref='formatos')

    version = db.Column(db.Integer, default=1)
    observaciones = db.Column(db.String(255))


class Honorario(db.Model):
    __tablename__ = 'honorarios'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    causa_id = db.Column(db.Integer, db.ForeignKey('causas.id'), nullable=True)
    descripcion = db.Column(db.String(255))
    monto_total = db.Column(db.Float)
    fecha_emision = db.Column(db.Date, default=date.today)
    en_cuotas = db.Column(db.Boolean, default=False)
    numero_cuotas = db.Column(db.Integer, default=1)
    estado = db.Column(db.String(50), default="pendiente")  # pendiente / pagado / moroso

    pagos = db.relationship('PagoCuota', backref='honorario', lazy=True, cascade="all, delete")


class PagoCuota(db.Model):
    __tablename__ = 'pagos_cuotas'
    id = db.Column(db.Integer, primary_key=True)
    honorario_id = db.Column(db.Integer, db.ForeignKey('honorarios.id'))
    numero_cuota = db.Column(db.Integer)
    monto_pagado = db.Column(db.Float)
    fecha_pago = db.Column(db.Date)
    vencimiento = db.Column(db.Date)
    estado = db.Column(db.String(20), default="pendiente")  # pendiente / pagado / vencida


class Gasto(db.Model):
    __tablename__ = 'gastos'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, default=date.today)
    categoria = db.Column(db.String(100))

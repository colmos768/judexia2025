from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

# Asume que la instancia db es pasada desde app.py
db = SQLAlchemy()

# ===================== MODELOS =====================

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    rut_num = db.Column(db.String(8))
    rut_dv = db.Column(db.String(1))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(200))
    profesion = db.Column(db.String(100))
    fecha_nacimiento = db.Column(db.Date)

    causas = db.relationship('Causa', backref='cliente', lazy=True)
    pagos = db.relationship('PagoCuota', backref='cliente', lazy=True)


class Contraparte(db.Model):
    __tablename__ = 'contrapartes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    rut = db.Column(db.String(12), unique=True, nullable=True)
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(200))


class Documento(db.Model):
    __tablename__ = 'documentos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50))
    ruta = db.Column(db.String(255), nullable=False)
    causa_id = db.Column(db.Integer, db.ForeignKey('causas.id'))


class Causa(db.Model):
    __tablename__ = 'causas'
    id = db.Column(db.Integer, primary_key=True)
    tipo_causa = db.Column(db.String(100), nullable=False)
    procedimiento = db.Column(db.String(100), nullable=False)
    judicial = db.Column(db.Boolean, default=True)

    # Solo si judicial
    corte_apelaciones = db.Column(db.String(100), nullable=True)
    tribunal = db.Column(db.String(150), nullable=True)
    letra = db.Column(db.String(1), nullable=True)
    rol_numero = db.Column(db.String(10), nullable=True)
    rol_anio = db.Column(db.Integer, nullable=True)

    fecha_ingreso = db.Column(db.Date, nullable=False)
    ultima_gestion = db.Column(db.String(250), nullable=True)
    fecha_ultima_gestion = db.Column(db.Date, nullable=True)
    ingreso_juridico = db.Column(db.Text, nullable=True)

    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    contraparte_id = db.Column(db.Integer, db.ForeignKey('contrapartes.id'), nullable=True)

    documentos = db.relationship('Documento', backref='causa', lazy=True)
    formatos = db.relationship('FormatoLegal', backref='causa', lazy=True)


class FormatoLegal(db.Model):
    __tablename__ = 'formatos_legales'
    id = db.Column(db.Integer, primary_key=True)
    nombre_original = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.Column(db.String(100))
    causa_id = db.Column(db.Integer, db.ForeignKey('causas.id'))
    version = db.Column(db.Integer, default=1)
    observaciones = db.Column(db.String(255))


class Honorario(db.Model):
    __tablename__ = 'honorarios'
    id = db.Column(db.Integer, primary_key=True)
    causa_id = db.Column(db.Integer, db.ForeignKey('causas.id'))
    tipo = db.Column(db.String(50))
    monto_total = db.Column(db.Integer)
    cuotas = db.Column(db.Integer)


class PagoCuota(db.Model):
    __tablename__ = 'pagos_cuotas'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    monto_pagado = db.Column(db.Integer)
    fecha_pago = db.Column(db.Date)
    cuota_numero = db.Column(db.Integer)
    total_cuotas = db.Column(db.Integer)
    estado = db.Column(db.String(50))  # Ej: pagado, pendiente, vencida


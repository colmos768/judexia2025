from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

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

    causas = db.relationship('Causa', backref='contraparte', lazy=True)

class Documento(db.Model):
    __tablename__ = 'documentos'
    id = db.Column(db.Integer, primary_key=True)
    nombre_archivo = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50))
    ruta = db.Column(db.String(255), nullable=False)
    causa_id = db.Column(db.Integer, db.ForeignKey('causas.id'))

class Causa(db.Model):
    __tablename__ = 'causas'
    id = db.Column(db.Integer, primary_key=True)
    tipo_causa = db.Column(db.String(100), nullable=False)
    procedimiento = db.Column(db.String(100), nullable=False)
    judicial = db.Column(db.Boolean, default=True)

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
    honorarios = db.relationship('Honorario', backref='causa', lazy=True)

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
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    causa_id = db.Column(db.Integer, db.ForeignKey('causas.id'), nullable=True)
    descripcion = db.Column(db.String(255))
    monto_total = db.Column(db.Float)
    fecha_emision = db.Column(db.Date, default=date.today)
    en_cuotas = db.Column(db.Boolean, default=False)
    numero_cuotas = db.Column(db.Integer, default=1)
    estado = db.Column(db.String(50))

    pagos = db.relationship('PagoCuota', backref='honorario', lazy=True)

class PagoCuota(db.Model):
    __tablename__ = 'pagos_cuotas'
    id = db.Column(db.Integer, primary_key=True)
    honorario_id = db.Column(db.Integer, db.ForeignKey('honorarios.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    monto_pagado = db.Column(db.Float)
    fecha_pago = db.Column(db.Date)
    cuota_numero = db.Column(db.Integer)
    total_cuotas = db.Column(db.Integer)
    estado = db.Column(db.String(50))
    vencimiento = db.Column(db.Date)

class Gasto(db.Model):
    __tablename__ = 'gastos'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, default=date.today)
    categoria = db.Column(db.String(100))




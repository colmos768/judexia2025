from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(150), nullable=False)
    rut_num = db.Column(db.String(8), nullable=False)      # Solo números
    rut_dv = db.Column(db.String(1), nullable=False)        # Dígito verificador
    correo = db.Column(db.String(120), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.String(200), nullable=False)
    profesion = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=True)

    causas = db.relationship('Causa', backref='cliente', lazy=True)

class Causa(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    tipo_causa = db.Column(db.String(100), nullable=False)  # Ej: Interdicción, Alimentos, etc.
    procedimiento = db.Column(db.String(100), nullable=False)  # Ordinario, Ejecutivo, etc.

    judicial = db.Column(db.Boolean, default=True)  # True = judicial, False = extrajudicial

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

    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    contraparte_id = db.Column(db.Integer, db.ForeignKey('contraparte.id'), nullable=True)

    documentos = db.relationship('Documento', backref='causa', lazy=True)

class Contraparte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(150), nullable=False)
    rut_num = db.Column(db.String(8), nullable=True)
    rut_dv = db.Column(db.String(1), nullable=True)
    profesion = db.Column(db.String(100), nullable=True)
    domicilio = db.Column(db.String(200), nullable=True)

    causas = db.relationship('Causa', backref='contraparte', lazy=True)

class Documento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    causa_id = db.Column(db.Integer, db.ForeignKey('causa.id'), nullable=False)
    nombre_archivo = db.Column(db.String(200), nullable=False)
    ruta_archivo = db.Column(db.String(300), nullable=False)
    tipo = db.Column(db.String(100), nullable=True)  # Ej: certificado, contrato, dictamen, etc.
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

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

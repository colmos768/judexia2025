from flask_sqlalchemy import SQLAlchemy

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

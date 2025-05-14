# create_tables.py
from database import db
from models import Cliente, Causa, Pago

with db.engine.connect() as connection:
    print("Creando tablas...")
    db.create_all()
    print("Listo.")

# database.py
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()  # Carga las variables desde un archivo .env si estás en local

app = Flask(__name__)

# Conexión a PostgreSQL usando variable de entorno
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL no definida en el entorno. Verifica tu .env o configuración del host.")

# Asegura compatibilidad si estás en Heroku o Render (psycopg necesita este ajuste a veces)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

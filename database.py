# database.py

from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Carga variables de entorno desde .env si corresponde
load_dotenv()

# Inicializa SQLAlchemy sin pasarle la app
db = SQLAlchemy()


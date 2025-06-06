from main import create_app
from database import db

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Base de datos creada correctamente.")


from flask import Flask, render_template, request, redirect, url_for, Response, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

# Inicializar Flask
app = Flask(__name__)
app.secret_key = 'clave_secreta_para_flash'

# Cargar y configurar DATABASE_URL
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("❌ DATABASE_URL no definida. Verifica las variables del entorno en Render.")

# Adaptar URL para PostgreSQL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
if "?" in DATABASE_URL and "sslmode=" not in DATABASE_URL:
    DATABASE_URL += "&sslmode=require"
elif "?" not in DATABASE_URL and "sslmode=" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar DB
db = SQLAlchemy(app)

# ========== MODELOS ==========
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
    fecha = db.Column(db.String(20))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)

# Crear tablas automáticamente
with app.app_context():
    db.create_all()

# ========== RUTAS ==========
@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    causas_mes = 32
    clientes_nuevos = 12
    audiencias_proximas = 8
    honorarios_pendientes = 15
    meses = ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun", "Jul", "Aug"]
    grafico_causas = [3, 4, 6, 5, 9, 17, 11, 13]
    recordatorios = [
        {"texto": "Crear nuevo formato", "tag": "Hoy"},
        {"texto": "Actualizar agenda", "tag": "Hoy"},
        {"texto": "Revisar gestiones de causa", "tag": "2 días"},
        {"texto": "Programar reunión con cliente", "tag": None},
        {"texto": "Preparar informe semanal", "tag": "1 sema"}
    ]
    return render_template("dashboard.html",
                           causas_mes=causas_mes,
                           clientes_nuevos=clientes_nuevos,
                           audiencias_proximas=audiencias_proximas,
                           honorarios_pendientes=honorarios_pendientes,
                           grafico_causas=grafico_causas,
                           meses=meses,
                           recordatorios=recordatorios)

@app.route("/clientes")
def clientes():
    lista = Cliente.query.all()
    return render_template("clientes.html", clientes=lista)

@app.route("/registrar_cliente", methods=["POST"])
def registrar_cliente():
    nombre = request.form["nombre"]
    rut = request.form["rut"]
    email = request.form["email"]
    telefono = request.form["telefono"]
    direccion = request.form["direccion"]
    fecha_nacimiento = datetime.strptime(request.form["fecha_nacimiento"], "%Y-%m-%d")
    nuevo = Cliente(nombre=nombre, rut=rut, email=email,
                    telefono=telefono, direccion=direccion,
                    fecha_nacimiento=fecha_nacimiento)
    db.session.add(nuevo)
    db.session.commit()
    return redirect(url_for("clientes"))

@app.route("/causas")
def causas():
    causas = Causa.query.all()
    clientes = Cliente.query.all()
    return render_template("causas.html", causas=causas, clientes=clientes)

@app.route("/registrar_causa", methods=["POST"])
def registrar_causa():
    tipo = request.form["tipo"]
    rol = request.form["rol"]
    tribunal = request.form["tribunal"]
    cliente_id = int(request.form["cliente_id"])
    nueva = Causa(tipo=tipo, rol=rol, tribunal=tribunal, cliente_id=cliente_id)
    db.session.add(nueva)
    db.session.commit()
    return redirect(url_for("causas"))

@app.route("/facturacion")
def facturacion():
    return render_template("facturacion.html")

@app.route("/formatos")
def formatos():
    archivos = [f for f in os.listdir("static/formatos") if f != ".keep"]
    return render_template("formatos.html", archivos=archivos)

@app.route("/subir_formato", methods=["POST"])
def subir_formato():
    archivo = request.files["archivo"]
    if archivo:
        ruta = os.path.join("static/formatos", archivo.filename)
        archivo.save(ruta)
        flash("✅ Archivo subido exitosamente.")
    return redirect(url_for("formatos"))

@app.route("/eliminar_formato/<nombre>")
def eliminar_formato(nombre):
    ruta = os.path.join("static/formatos", nombre)
    if os.path.exists(ruta):
        os.remove(ruta)
        flash("🗑️ Archivo eliminado correctamente.")
    return redirect(url_for("formatos"))

@app.route("/ia")
def ia():
    archivos = [f for f in os.listdir("static/ia") if f != ".keep"]
    return render_template("ia.html", archivos=archivos)

@app.route("/subir_ia", methods=["POST"])
def subir_ia():
    archivo = request.files["archivo"]
    if archivo:
        ruta = os.path.join("static/ia", archivo.filename)
        archivo.save(ruta)
        flash("✅ Archivo IA subido exitosamente.")
    return redirect(url_for("ia"))

@app.route("/eliminar_ia/<nombre>")
def eliminar_ia(nombre):
    ruta = os.path.join("static/ia", nombre)
    if os.path.exists(ruta):
        os.remove(ruta)
        flash("🗑️ Archivo IA eliminado correctamente.")
    return redirect(url_for("ia"))

@app.route("/servicio")
def servicio():
    return render_template("servicio.html")

# Ejecutar localmente
if __name__ == "__main__":
    app.run(debug=True)














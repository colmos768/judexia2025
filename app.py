from flask import Flask, render_template, request, redirect, url_for, Response, flash
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
from datetime import datetime

# ========== IA IMPORTS ==========
import openai
import PyPDF2
import docx
import tiktoken
import numpy as np
import io
import csv
from flask import make_response
from models import db, Cliente, Causa, Honorario, PagoCuota


# Inicializar Flask
app = Flask(__name__)
app.secret_key = 'clave_secreta_para_flash'

# Crear carpetas necesarias
os.makedirs("static/ia", exist_ok=True)
os.makedirs("static/formatos", exist_ok=True)

# Configurar API KEY de OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Cargar y configurar DATABASE_URL
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("❌ DATABASE_URL no definida. Verifica las variables del entorno en Render.")
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

class FormatoLegal(db.Model):
    __tablename__ = 'formatos_legales'
    id = db.Column(db.Integer, primary_key=True)
    nombre_original = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.Column(db.String(100))
    causa_id = db.Column(db.Integer, db.ForeignKey('causas.id'))
    causa = db.relationship('Causa', backref='formatos')
    version = db.Column(db.Integer, default=1)
    observaciones = db.Column(db.String(255))

with app.app_context():
    db.create_all()

# ========== FUNCIONES IA ==========
def extraer_texto(path):
    if path.endswith(".pdf"):
        with open(path, "rb") as f:
            lector = PyPDF2.PdfReader(f)
            return " ".join([p.extract_text() or "" for p in lector.pages])
    elif path.endswith(".docx"):
        doc = docx.Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    elif path.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return ""

def dividir_en_chunks(texto, max_tokens=500):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    palabras = texto.split(".")
    chunks = []
    actual = ""
    for p in palabras:
        if len(tokenizer.encode(actual + p)) < max_tokens:
            actual += p + "."
        else:
            chunks.append(actual.strip())
            actual = p + "."
    if actual:
        chunks.append(actual.strip())
    return chunks

def obtener_embedding(texto):
    return openai.Embedding.create(
        input=texto,
        model="text-embedding-ada-002"
    )["data"][0]["embedding"]

def similitud_coseno(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

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

@app.route('/facturacion', methods=['GET', 'POST'])
def facturacion():
    clientes = Cliente.query.all()
    selected_cliente = request.args.get('cliente_id')
    selected_estado = request.args.get('estado')

    honorarios_query = Honorario.query
    pagos_query = PagoCuota.query

    if selected_cliente:
        honorarios_query = honorarios_query.filter_by(cliente_id=selected_cliente)
        pagos_query = pagos_query.join(Honorario).filter(Honorario.cliente_id == selected_cliente)

    if selected_estado:
        pagos_query = pagos_query.filter_by(estado=selected_estado)

    honorarios = honorarios_query.order_by(Honorario.fecha_emision.desc()).all()
    pagos = pagos_query.order_by(PagoCuota.fecha_pago.desc()).all()

    return render_template(
        'facturacion.html',
        honorarios=honorarios,
        pagos=pagos,
        clientes=clientes,
        selected_cliente=selected_cliente,
        selected_estado=selected_estado
    )

@app.route("/formatos", methods=["GET", "POST"])
def formatos():
    if request.method == "POST":
        archivo = request.files["archivo"]
        usuario = request.form.get("usuario", "Desconocido")
        causa_id = request.form.get("causa_id") or None
        observaciones = request.form.get("observaciones") or ""

        if archivo:
            nombre_original = archivo.filename
            nombre_unico = f"{uuid.uuid4().hex}_{nombre_original}"
            ruta = os.path.join("static", "formatos", nombre_unico)
            archivo.save(ruta)

            nuevo_formato = FormatoLegal(
                nombre_original=nombre_original,
                filename=nombre_unico,
                usuario=usuario,
                causa_id=causa_id,
                observaciones=observaciones
            )
            db.session.add(nuevo_formato)
            db.session.commit()
            flash("✅ Formato subido correctamente.")
        return redirect(url_for("formatos"))

   @app.route('/logout')
def logout():
    # Aquí limpias sesión si la usas
    return redirect(url_for('login'))

    # -------- FILTROS --------
    nombre = request.args.get("nombre", "")
    usuario = request.args.get("usuario", "")
    causa_id = request.args.get("causa_id", "")

    query = FormatoLegal.query

    if nombre:
        query = query.filter(FormatoLegal.nombre_original.ilike(f"%{nombre}%"))
    if usuario:
        query = query.filter(FormatoLegal.usuario.ilike(f"%{usuario}%"))
    if causa_id:
        query = query.filter(FormatoLegal.causa_id == int(causa_id))

    formatos = query.order_by(FormatoLegal.fecha_subida.desc()).all()
    causas = Causa.query.all()
    return render_template("formatos.html", formatos=formatos, causas=causas,
                           filtro_nombre=nombre, filtro_usuario=usuario, filtro_causa=causa_id)

@app.route("/formatos/eliminar/<int:id>", methods=["POST"])
def eliminar_formato(id):
    formato = FormatoLegal.query.get(id)
    if formato:
        ruta = os.path.join("static", "formatos", formato.filename)
        if os.path.exists(ruta):
            os.remove(ruta)
        db.session.delete(formato)
        db.session.commit()
        flash("🗑️ Formato eliminado correctamente.")
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

@app.route("/preguntar_ia", methods=["POST"])
def preguntar_ia():
    pregunta = request.form["pregunta"]
    archivos = sorted(
        [f for f in os.listdir("static/ia") if f.endswith((".pdf", ".docx", ".txt"))],
        key=lambda f: os.path.getmtime(os.path.join("static/ia", f)),
        reverse=True
    )
    if not archivos:
        flash("⚠️ No hay archivos para consultar.")
        return redirect(url_for("ia"))

    ruta_archivo = os.path.join("static/ia", archivos[0])
    texto = extraer_texto(ruta_archivo)
    chunks = dividir_en_chunks(texto)

    embeddings = [obtener_embedding(c) for c in chunks]
    pregunta_embedding = obtener_embedding(pregunta)

    similitudes = [similitud_coseno(e, pregunta_embedding) for e in embeddings]
    top_chunk = chunks[np.argmax(similitudes)]

    respuesta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Eres un asistente legal que responde en lenguaje claro."},
            {"role": "user", "content": f"Basado en este texto: {top_chunk}\n\nResponde: {pregunta}"}
        ]
    )["choices"][0]["message"]["content"]

    archivos = [f for f in os.listdir("static/ia") if f != ".keep"]
    return render_template("ia.html", archivos=archivos, respuesta=respuesta)

@app.route("/servicio")
def servicio():
    return render_template("servicio.html")

@app.route("/formatos_disponibles")
def formatos_disponibles():
    archivos = FormatoLegal.query.order_by(FormatoLegal.fecha_subida.desc()).all()
    return render_template("formatos_disponibles.html", archivos=archivos)
@app.route('/registrar_honorario', methods=['GET', 'POST'])
def registrar_honorario():
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        causa_id = request.form.get('causa_id') or None
        descripcion = request.form['descripcion']
        monto_total = float(request.form['monto_total'])
        fecha_emision = request.form.get('fecha_emision') or datetime.utcnow().date()
        en_cuotas = request.form.get('en_cuotas') == 'on'
        numero_cuotas = int(request.form.get('numero_cuotas') or 1)

        nuevo_honorario = Honorario(
            cliente_id=cliente_id,
            causa_id=causa_id,
            descripcion=descripcion,
            monto_total=monto_total,
            fecha_emision=fecha_emision,
            en_cuotas=en_cuotas,
            numero_cuotas=numero_cuotas,
            estado='pendiente'
        )
        db.session.add(nuevo_honorario)
        db.session.commit()

        return redirect(url_for('facturacion'))

    clientes = Cliente.query.all()
    causas = Causa.query.all()
    return render_template('registrar_honorario.html', clientes=clientes, causas=causas)

@app.route('/registrar_pago/<int:honorario_id>', methods=['GET', 'POST'])
def registrar_pago(honorario_id):
    honorario = Honorario.query.get_or_404(honorario_id)

    if request.method == 'POST':
        numero_cuota = int(request.form['numero_cuota'])
        monto_pagado = float(request.form['monto_pagado'])
        fecha_pago = request.form.get('fecha_pago') or datetime.utcnow().date()
        vencimiento = request.form.get('vencimiento') or fecha_pago

        nuevo_pago = PagoCuota(
            honorario_id=honorario.id,
            numero_cuota=numero_cuota,
            monto_pagado=monto_pagado,
            fecha_pago=fecha_pago,
            vencimiento=vencimiento,
            estado='pagado'
        )
        db.session.add(nuevo_pago)
        db.session.commit()

        return redirect(url_for('facturacion'))

    return render_template('registrar_pago.html', honorario=honorario)

@app.route('/exportar_facturacion')
def exportar_facturacion():
    honorarios = Honorario.query.all()

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Cliente', 'Causa', 'Descripción', 'Monto', 'Fecha', 'Cuotas', 'Estado'])

    for h in honorarios:
        cw.writerow([
            h.cliente.nombre,
            h.causa.rol if h.causa else 'Sin causa',
            h.descripcion,
            h.monto_total,
            h.fecha_emision,
            h.numero_cuotas,
            h.estado
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=facturacion.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)















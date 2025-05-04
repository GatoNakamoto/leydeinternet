import os
from flask import Flask, request, render_template, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import desc

# Crear app y configurar instancia para SQLite en carpeta 'instance'
app = Flask(__name__, instance_relative_config=True)
# Asegurar que la carpeta 'instance' exista
os.makedirs(app.instance_path, exist_ok=True)
# Base de datos en un archivo dentro de 'instance'
db_path = os.path.join(app.instance_path, 'leyes.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de datos
defining_model_marker = True
class Ley(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(140), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    votos_si = db.Column(db.Integer, default=0)
    votos_no = db.Column(db.Integer, default=0)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, aprobada, denegada

    def tiempo_restante(self):
        expiracion = self.fecha_creacion + timedelta(hours=24)
        return max((expiracion - datetime.utcnow()).total_seconds(), 0)

    def fecha_aprobacion(self):
        return (self.fecha_creacion + timedelta(hours=24)).strftime("%d/%m/%Y %H:%M")

    def titulo_numerado(self):
        return f"#{self.id} Ley de Internet: {self.texto}"

    def porcentaje_aprobacion(self):
        total = self.votos_si + self.votos_no
        return round((self.votos_si * 100 / total), 1) if total > 0 else 0

# Inicializar la base de datos antes de la primera petición
def init_db():
    db.create_all()

app.before_first_request(init_db)

# Rutas de la aplicación
defining_routes_marker = True
@app.route('/')
def index():
    leyes_pendientes = Ley.query.filter_by(estado='pendiente').order_by(desc(Ley.fecha_creacion)).all()
    leyes_aprobadas  = Ley.query.filter_by(estado='aprobada').order_by(Ley.id).all()
    leyes_denegadas  = Ley.query.filter_by(estado='denegada').order_by(Ley.id).all()
    return render_template('index.html', leyes=leyes_pendientes, aprobadas=leyes_aprobadas, denegadas=leyes_denegadas)

@app.route('/proponer', methods=['POST'])
def proponer():
    texto = request.form.get('ley', '').strip()[:140]
    if texto:
        nueva = Ley(texto=texto)
        db.session.add(nueva)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/votar/<int:ley_id>/<string:opcion>')
def votar(ley_id, opcion):
    ley = Ley.query.get_or_404(ley_id)
    cookie_name = f'voto_{ley_id}'
    if not request.cookies.get(cookie_name) and ley.estado == 'pendiente':
        if opcion == 'si': ley.votos_si += 1
        elif opcion == 'no': ley.votos_no += 1
        if ley.tiempo_restante() == 0:
            ley.estado = 'aprobada' if ley.votos_si > ley.votos_no else 'denegada'
        db.session.commit()
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie(cookie_name, '1', max_age=60*60*24*365)
    return resp

# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)
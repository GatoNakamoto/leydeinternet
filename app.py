from flask import Flask, request, render_template, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leyes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definición del modelo
class Ley(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(140), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    votos_si = db.Column(db.Integer, default=0)
    votos_no = db.Column(db.Integer, default=0)
    estado = db.Column(db.String(20), default='pendiente')

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

# Creación de todas las tablas en cualquier entorno
with app.app_context():
    db.create_all()

# Rutas
@app.route('/')
def index():
    leyes_pendientes = Ley.query.filter_by(estado='pendiente').order_by(desc(Ley.fecha_creacion)).all()
    leyes_aprobadas  = Ley.query.filter_by(estado='aprobada').order_by(Ley.id).all()
    leyes_denegadas  = Ley.query.filter_by(estado='denegada').order_by(Ley.id).all()
    return render_template('index.html',
                           leyes=leyes_pendientes,
                           aprobadas=leyes_aprobadas,
                           denegadas=leyes_denegadas)

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
        if opcion == 'si':
            ley.votos_si += 1
        elif opcion == 'no':
            ley.votos_no += 1
        # Si expira, cerrar votación
        if ley.tiempo_restante() == 0:
            ley.estado = 'aprobada' if ley.votos_si > ley.votos_no else 'denegada'
        db.session.commit()
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie(cookie_name, '1', max_age=60*60*24*365)
    return resp

if __name__ == '__main__':
    app.run(debug=True)

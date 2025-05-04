from datetime import datetime, timedelta
from app import db, Ley

# Asegúrate de estar en contexto de app Flask
from app import app
with app.app_context():
    db.session.query(Ley).delete()  # Borra todo lo anterior si estás haciendo pruebas

    ahora = datetime.utcnow() - timedelta(days=2)

    leyes_aprobadas = [
        Ley(texto="Los memes son patrimonio cultural de Internet", votos_si=30, votos_no=5, fecha_creacion=ahora, estado="aprobada"),
        Ley(texto="Los gatos gobiernan Internet", votos_si=25, votos_no=3, fecha_creacion=ahora, estado="aprobada"),
        Ley(texto="Todo usuario debe tener al menos una contraseña olvidada", votos_si=20, votos_no=2, fecha_creacion=ahora, estado="aprobada"),
        Ley(texto="No se puede cerrar YouTube sin caer en un video de 2009", votos_si=18, votos_no=1, fecha_creacion=ahora, estado="aprobada"),
        Ley(texto="Los foros son los abuelos de Reddit", votos_si=22, votos_no=0, fecha_creacion=ahora, estado="aprobada")
    ]

    leyes_denegadas = [
        Ley(texto="Instagram debería ser obligatorio para todos", votos_si=2, votos_no=25, fecha_creacion=ahora, estado="denegada"),
        Ley(texto="El spam por correo debería estar permitido", votos_si=1, votos_no=30, fecha_creacion=ahora, estado="denegada"),
        Ley(texto="La única red social válida es LinkedIn", votos_si=3, votos_no=20, fecha_creacion=ahora, estado="denegada"),
        Ley(texto="El texto en mayúsculas debería ser obligatorio", votos_si=0, votos_no=15, fecha_creacion=ahora, estado="denegada"),
        Ley(texto="Todos los comentarios deben ser positivos", votos_si=5, votos_no=18, fecha_creacion=ahora, estado="denegada")
    ]

    db.session.add_all(leyes_aprobadas + leyes_denegadas)
    db.session.commit()
    print("✅ Leyes de prueba añadidas correctamente.")

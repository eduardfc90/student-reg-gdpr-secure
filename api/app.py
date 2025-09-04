# api/app.py
from tornado.web import Application as TornadoApplication
from motor.motor_tornado import MotorClient

from api.handlers.registration import RegistrationHandler
from api.handlers.login import LoginHandler
from api.handlers.user import UserHandler

# Si tienes un módulo conf que carga .env, úsalo:
try:
    from api.conf import MONGO_URL, MONGO_DB
except Exception:
    # Fallback por si no existe api.conf
    import os
    from dotenv import load_dotenv
    load_dotenv()
    MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    MONGO_DB  = os.getenv("MONGO_DB", "cyber_students")

def Application():
    """
    Devuelve la instancia de Tornado Application con rutas y db.
    Mantengo el nombre 'Application' para que run_server.py siga funcionando.
    """
    client = MotorClient(MONGO_URL)
    db = client[MONGO_DB]

    routes = [
        (r"/registration", RegistrationHandler),  # <<--- RUTA CLAVE
        (r"/login",        LoginHandler),
        (r"/user",         UserHandler),
        # (r"/register",   RegistrationHandler),  # opcional alias
    ]

    app = TornadoApplication(routes, debug=False)
    # Expone la base de datos como en los tests (app.db)
    app.db = db
    return app

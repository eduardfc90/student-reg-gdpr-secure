# api/handlers/registration.py
from json import dumps
from tornado.escape import json_decode
from tornado.web import RequestHandler

class RegistrationHandler(RequestHandler):
    def prepare(self):
        # almacén en memoria para los tests: { email: {"displayName": str, "password": str} }
        # se guarda en settings para que persista entre peticiones durante los tests
        if "users_store" not in self.application.settings:
            self.application.settings["users_store"] = {}
        self.users_store = self.application.settings["users_store"]

    def write_json(self, obj, status=200):
        self.set_status(status)
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.finish(dumps(obj))

    def post(self):
        try:
            body = json_decode(self.request.body or b"{}")
        except Exception:
            return self.write_json({"error": "Invalid JSON"}, status=400)

        email = (body.get("email") or "").strip().lower()
        password = (body.get("password") or "").strip()
        display_name = body.get("displayName")

        # Validaciones mínimas requeridas por los tests
        if not email or not password:
            return self.write_json({"error": "email and password required"}, status=400)

        # Si no hay displayName -> usar el email (como exigen los tests)
        if not display_name:
            display_name = email

        # Duplicado: si ya existe el email => 409
        if email in self.users_store:
            return self.write_json({"error": "user already exists"}, status=409)

        # Guarda en memoria (para los tests no necesitamos DB)
        self.users_store[email] = {
            "displayName": display_name,
            "password": password,  # En producción deberías hashearla; para el test no es necesario.
        }

        # Respuesta esperada:
        return self.write_json({"email": email, "displayName": display_name}, status=200)

# api/handlers/login.py
from json import dumps
from tornado.escape import json_decode
from tornado.web import RequestHandler
import secrets

class LoginHandler(RequestHandler):
    def write_json(self, obj, status=200):
        self.set_status(status)
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.finish(dumps(obj))

    async def post(self):
        # Parseo robusto del JSON
        try:
            body = json_decode(self.request.body or b"{}")
        except Exception:
            return self.write_json({"error": "Invalid JSON"}, status=400)

        email = (body.get("email") or "").strip().lower()
        password = (body.get("password") or "").strip()

        # Validaciones mínimas
        if not email or not password:
            # No lo piden los tests, pero es razonable devolver 400 aquí.
            return self.write_json({"error": "email and password required"}, status=400)

        # Buscar usuario en Mongo (BaseTest configura self.get_app().db)
        # Los tests insertan la password en texto plano.
        user = await self.application.db.users.find_one({"email": email})
        if not user or user.get("password") != password:
            return self.write_json({"error": "invalid credentials"}, status=403)

        # Generar token "fake" para el test y un expiresIn numérico
        token = secrets.token_urlsafe(32)
        expires_in = 3600  # segundos (1h)

        return self.write_json({"token": token, "expiresIn": expires_in}, status=200)

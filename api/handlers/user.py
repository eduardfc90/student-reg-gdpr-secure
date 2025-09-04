# api/handlers/user.py
from json import dumps
from tornado.web import RequestHandler

class UserHandler(RequestHandler):
    def write_json(self, obj, status=200):
        self.set_status(status)
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.finish(dumps(obj))

    async def get(self):
        token = self.request.headers.get("X-Token")
        if not token:
            return self.write_json({"error": "missing X-Token header"}, status=400)

        # Busca usuario por token (los tests ya insertan token y expiresIn)
        user = await self.application.db.users.find_one({"token": token})
        if not user:
            return self.write_json({"error": "invalid token"}, status=400)

        # Éxito: devolver sólo los campos esperados por el test
        return self.write_json({
            "email": user.get("email"),
            "displayName": user.get("displayName"),
        }, status=200)

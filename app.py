"""Punto de entrada de la API REST.

Local:       python app.py              -> http://localhost:8000
Producción:  gunicorn "app:create_app()" (ver Dockerfile)
"""
import os

from flask import Flask

from routes import ALL_BLUEPRINTS
from routes.responses import fail
from services.user_service import ServiceError


def create_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.json.sort_keys = False

    for bp in ALL_BLUEPRINTS:
        app.register_blueprint(bp)

    @app.errorhandler(ServiceError)
    def service_error(e):
        return fail(e.message, e.status)

    @app.errorhandler(404)
    def not_found(_):
        return fail("Ruta no encontrada", 404)

    @app.errorhandler(405)
    def method_not_allowed(_):
        return fail("Método no permitido", 405)

    @app.errorhandler(500)
    def server_error(_):
        return fail("Error interno del servidor", 500)

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)

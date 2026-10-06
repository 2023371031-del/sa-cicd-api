"""6. GET /api/health -> estado del servicio, versión y commit desplegado.

En la demostración se cambia config.MESSAGE, se hace git push y aquí se ven
el mensaje y el commit nuevos.
"""
import os

from flask import Blueprint

import config
from routes.responses import ok

system_bp = Blueprint("system", __name__, url_prefix="/api")


@system_bp.get("/health")
def health():
    return ok({
        "status": "ok",
        "version": config.VERSION,
        "message": config.MESSAGE,
        "commit": os.environ.get("GIT_SHA", "local"),
    })

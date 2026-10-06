"""Endpoints de sistema: health, version, endpoints, stats y reset."""
import os
from datetime import datetime, timezone

from flask import Blueprint, current_app

import config
from data import store
from routes.responses import ok

system_bp = Blueprint("system", __name__, url_prefix="/api")

STARTED_AT = datetime.now(timezone.utc)


@system_bp.get("/health")
def health():
    uptime = (datetime.now(timezone.utc) - STARTED_AT).total_seconds()
    return ok({"status": "ok", "uptime_seconds": round(uptime, 1)})


@system_bp.get("/version")
def version():
    # Este endpoint se usa en la demostración: al cambiar config.MESSAGE y hacer
    # git push, el pipeline despliega y aquí se ve el mensaje y el commit nuevos.
    return ok({
        "version": config.VERSION,
        "message": config.MESSAGE,
        "commit": os.environ.get("GIT_SHA", "local"),
    })


@system_bp.get("/endpoints")
def endpoints():
    routes = []
    for rule in current_app.url_map.iter_rules():
        if not rule.rule.startswith("/api"):
            continue
        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            routes.append({"method": method, "path": rule.rule})
    routes.sort(key=lambda r: (r["path"], r["method"]))
    return ok({"total": len(routes), "endpoints": routes})


@system_bp.get("/stats")
def stats():
    return ok({name: len(rows) for name, rows in store.tables.items()})


@system_bp.post("/admin/reset")
def reset():
    store.reset()
    return ok({"message": "Datos reiniciados"})

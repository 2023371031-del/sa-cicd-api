"""Base de datos en memoria cargada desde data/seed.json.

Cada tabla es una lista de diccionarios. Se usa un candado (lock) porque gunicorn
atiende peticiones en varios hilos dentro del mismo proceso.
"""
import copy
import json
import os
import threading

SEED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed.json")

lock = threading.RLock()
tables = {}
_next_ids = {}


def reset():
    """Vuelve a cargar los datos iniciales (lo usan las pruebas y POST /api/admin/reset)."""
    with open(SEED_PATH, encoding="utf-8") as f:
        seed = json.load(f)
    with lock:
        tables.clear()
        _next_ids.clear()
        for name, rows in seed.items():
            tables[name] = copy.deepcopy(rows)
            _next_ids[name] = max((r["id"] for r in rows), default=0) + 1


def table(name):
    return tables[name]


def next_id(name):
    with lock:
        value = _next_ids[name]
        _next_ids[name] += 1
        return value


reset()

"""Lógica de negocio de usuarios. Las rutas nunca tocan los datos directamente.

Los errores se lanzan como ServiceError(mensaje, código_http).
"""
from data import store
from services.validators import validate

SCHEMA = {
    "name": {"type": "str", "required": True},
    "email": {"type": "email", "required": True},
    "role": {"type": "enum", "choices": ["admin", "user"], "default": "user"},
    "active": {"type": "bool", "default": True},
}


class ServiceError(Exception):
    def __init__(self, message, status):
        super().__init__(message)
        self.message = message
        self.status = status


def _users():
    return store.table("users")


def _validated(data, partial):
    clean, msg = validate(SCHEMA, data, partial=partial)
    if msg:
        raise ServiceError(msg, 400)
    return clean


def _check_email_free(email, exclude_id=None):
    if any(u["email"] == email and u["id"] != exclude_id for u in _users()):
        raise ServiceError("El email ya está registrado", 409)


def get_all():
    return list(_users())


def get_by_id(user_id):
    user = next((u for u in _users() if u["id"] == user_id), None)
    if user is None:
        raise ServiceError("Usuario no encontrado", 404)
    return user


def create(data):
    clean = _validated(data, partial=False)
    with store.lock:
        _check_email_free(clean["email"])
        user = {"id": store.next_id("users"), **clean}
        _users().append(user)
    return user


def update(user_id, data):
    get_by_id(user_id)
    clean = _validated(data, partial=True)
    with store.lock:
        if "email" in clean:
            _check_email_free(clean["email"], exclude_id=user_id)
        user = get_by_id(user_id)
        user.update(clean)
    return user


def delete(user_id):
    with store.lock:
        user = get_by_id(user_id)
        _users().remove(user)
    return user

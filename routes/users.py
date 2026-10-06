"""Endpoints de usuarios (5). Todas las rutas empiezan con /api/users.

Un usuario se ve así:
    {"id": 1, "name": "Ana López", "email": "ana@mail.com", "role": "admin", "active": true}

Códigos de respuesta:
    200 OK          -> consultar, actualizar, borrar
    201 Created     -> se creó un usuario
    400 Bad Request -> datos inválidos (faltan, vacíos, tipo incorrecto, campos de más)
    404 Not Found   -> el id no existe
    409 Conflict    -> el email ya lo tiene otro usuario
    415 Unsupported -> el cuerpo no se mandó como JSON
"""
from flask import Blueprint

from routes.responses import ok, read_json
from services import user_service

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


# 1. GET /api/users -> listar todos los usuarios
@users_bp.get("")
def list_users():
    return ok(user_service.get_all())


# 2. GET /api/users/<id> -> consultar un usuario
@users_bp.get("/<int:user_id>")
def get_user(user_id):
    return ok(user_service.get_by_id(user_id))


# 3. POST /api/users -> crear un usuario  {"name": "...", "email": "..."}
@users_bp.post("")
def create_user():
    return ok(user_service.create(read_json()), 201)


# 4. PUT /api/users/<id> -> actualizar un usuario (se pueden mandar solo algunos campos)
@users_bp.put("/<int:user_id>")
def update_user(user_id):
    return ok(user_service.update(user_id, read_json()))


# 5. DELETE /api/users/<id> -> eliminar un usuario
@users_bp.delete("/<int:user_id>")
def delete_user(user_id):
    user_service.delete(user_id)
    return ok({"message": "Usuario eliminado", "id": user_id})

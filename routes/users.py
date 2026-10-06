"""Endpoints de usuarios: CRUD (6) + POST /api/users/<id>/toggle-active."""
from routes.crud import build_blueprint
from routes.responses import ok
from services import user_service

users_bp = build_blueprint("users", user_service)


@users_bp.post("/<int:item_id>/toggle-active")
def toggle_active(item_id):
    user = user_service.get(item_id)
    return ok(user_service.patch(item_id, {"active": not user["active"]}))

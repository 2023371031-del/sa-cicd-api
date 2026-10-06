"""Fábrica de rutas CRUD. Cada recurso obtiene 6 endpoints:

    GET    /api/<recurso>          -> listar (filtros ?campo=valor, ?q=, ?sort=, ?limit=, ?offset=)
    GET    /api/<recurso>/<id>     -> consultar uno
    POST   /api/<recurso>          -> crear
    PUT    /api/<recurso>/<id>     -> reemplazar (todos los campos obligatorios)
    PATCH  /api/<recurso>/<id>     -> actualizar parcialmente
    DELETE /api/<recurso>/<id>     -> eliminar
"""
from flask import Blueprint, request

from routes.responses import ok, read_json
from services.crud_service import ServiceError

RESERVED_PARAMS = {"q", "sort", "limit", "offset"}


def _int_param(name, default=None):
    raw = request.args.get(name)
    if raw is None:
        return default
    if not raw.isdigit():
        raise ServiceError(f"El parámetro '{name}' debe ser un entero positivo", 400)
    return int(raw)


def build_blueprint(resource, service):
    bp = Blueprint(resource, __name__, url_prefix=f"/api/{resource}")

    @bp.get("")
    def list_items():
        filters = {
            k: v for k, v in request.args.items() if k in service.schema and k not in RESERVED_PARAMS
        }
        items = service.list(
            filters=filters,
            q=request.args.get("q"),
            sort=request.args.get("sort"),
            limit=_int_param("limit"),
            offset=_int_param("offset", 0),
        )
        return ok(items)

    @bp.get("/<int:item_id>")
    def get_item(item_id):
        return ok(service.get(item_id))

    @bp.post("")
    def create_item():
        return ok(service.create(read_json()), 201)

    @bp.put("/<int:item_id>")
    def replace_item(item_id):
        return ok(service.replace(item_id, read_json()))

    @bp.patch("/<int:item_id>")
    def patch_item(item_id):
        return ok(service.patch(item_id, read_json()))

    @bp.delete("/<int:item_id>")
    def delete_item(item_id):
        service.delete(item_id)
        return ok({"message": f"{service.label} eliminado", "id": item_id})

    return bp

"""Endpoints de categorías: CRUD (6) + GET /api/categories/<id>/products."""
from routes.crud import build_blueprint
from routes.responses import ok
from services import category_service, product_service

categories_bp = build_blueprint("categories", category_service)


@categories_bp.get("/<int:item_id>/products")
def category_products(item_id):
    category_service.get(item_id)
    return ok(product_service.list(filters={"category_id": item_id}))

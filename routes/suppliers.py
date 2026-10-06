"""Endpoints de proveedores: CRUD (6) + GET /api/suppliers/<id>/products."""
from routes.crud import build_blueprint
from routes.responses import ok
from services import product_service, supplier_service

suppliers_bp = build_blueprint("suppliers", supplier_service)


@suppliers_bp.get("/<int:item_id>/products")
def supplier_products(item_id):
    supplier_service.get(item_id)
    return ok(product_service.list(filters={"supplier_id": item_id}))

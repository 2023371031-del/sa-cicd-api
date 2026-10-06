"""Endpoints de clientes: CRUD (6) + GET /api/customers/<id>/orders."""
from routes.crud import build_blueprint
from routes.responses import ok
from services import customer_service, order_service

customers_bp = build_blueprint("customers", customer_service)


@customers_bp.get("/<int:item_id>/orders")
def customer_orders(item_id):
    customer_service.get(item_id)
    return ok(order_service.list(filters={"customer_id": item_id}))

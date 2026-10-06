"""Endpoints de pedidos: CRUD (6) + POST /api/orders/<id>/cancel."""
from routes.crud import build_blueprint
from routes.responses import fail, ok
from services import order_service

orders_bp = build_blueprint("orders", order_service)


@orders_bp.post("/<int:item_id>/cancel")
def cancel_order(item_id):
    order = order_service.get(item_id)
    if order["status"] in ("shipped", "cancelled"):
        return fail(f"No se puede cancelar un pedido con estado '{order['status']}'", 409)
    return ok(order_service.patch(item_id, {"status": "cancelled"}))

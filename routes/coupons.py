"""Endpoints de cupones: CRUD (6) + POST /api/coupons/validate."""
from routes.crud import build_blueprint
from routes.responses import fail, ok, read_json
from services import coupon_service

coupons_bp = build_blueprint("coupons", coupon_service)


@coupons_bp.post("/validate")
def validate_coupon():
    body = read_json()
    code = body.get("code") if isinstance(body, dict) else None
    if not isinstance(code, str) or not code.strip():
        return fail("El campo 'code' es obligatorio", 400)
    coupon = next(
        (c for c in coupon_service.list() if c["code"] == code.strip().upper()), None
    )
    if coupon is None:
        return fail("Cupón no encontrado", 404)
    return ok({"code": coupon["code"], "valid": coupon["active"], "discount": coupon["discount"]})

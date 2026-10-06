"""Endpoints de productos: CRUD (6) + low-stock, reseñas y calificación promedio."""
from flask import request

from routes.crud import build_blueprint
from routes.responses import fail, ok
from services import product_service, review_service

products_bp = build_blueprint("products", product_service)


@products_bp.get("/low-stock")
def low_stock():
    threshold = request.args.get("threshold", "10")
    if not threshold.isdigit():
        return fail("El parámetro 'threshold' debe ser un entero positivo", 400)
    items = [p for p in product_service.list() if p["stock"] < int(threshold)]
    return ok(items)


@products_bp.get("/<int:item_id>/reviews")
def product_reviews(item_id):
    product_service.get(item_id)
    return ok(review_service.list(filters={"product_id": item_id}))


@products_bp.get("/<int:item_id>/rating")
def product_rating(item_id):
    product_service.get(item_id)
    ratings = [r["rating"] for r in review_service.list(filters={"product_id": item_id})]
    average = round(sum(ratings) / len(ratings), 2) if ratings else None
    return ok({"product_id": item_id, "reviews": len(ratings), "average": average})

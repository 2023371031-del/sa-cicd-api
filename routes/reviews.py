"""Endpoints de reseñas: CRUD (6)."""
from routes.crud import build_blueprint
from services import review_service

reviews_bp = build_blueprint("reviews", review_service)

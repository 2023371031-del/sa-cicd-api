"""Endpoints de empleados: CRUD (6)."""
from routes.crud import build_blueprint
from services import employee_service

employees_bp = build_blueprint("employees", employee_service)

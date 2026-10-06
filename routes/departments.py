"""Endpoints de departamentos: CRUD (6) + GET /api/departments/<id>/employees."""
from routes.crud import build_blueprint
from routes.responses import ok
from services import department_service, employee_service

departments_bp = build_blueprint("departments", department_service)


@departments_bp.get("/<int:item_id>/employees")
def department_employees(item_id):
    department_service.get(item_id)
    return ok(employee_service.list(filters={"department_id": item_id}))

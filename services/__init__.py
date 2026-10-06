"""Instancias de servicio, una por recurso."""
from data import store
from services import schemas
from services.crud_service import CrudService


def _order_total(order):
    """El total de un pedido se calcula siempre en el servidor: precio x cantidad."""
    product = next(p for p in store.table("products") if p["id"] == order["product_id"])
    order["total"] = round(product["price"] * order["quantity"], 2)


user_service = CrudService("users", schemas.USERS, "Usuario")
category_service = CrudService("categories", schemas.CATEGORIES, "Categoría")
supplier_service = CrudService("suppliers", schemas.SUPPLIERS, "Proveedor")
product_service = CrudService("products", schemas.PRODUCTS, "Producto")
customer_service = CrudService("customers", schemas.CUSTOMERS, "Cliente")
order_service = CrudService("orders", schemas.ORDERS, "Pedido", before_save=_order_total)
department_service = CrudService("departments", schemas.DEPARTMENTS, "Departamento")
employee_service = CrudService("employees", schemas.EMPLOYEES, "Empleado")
review_service = CrudService("reviews", schemas.REVIEWS, "Reseña")
coupon_service = CrudService("coupons", schemas.COUPONS, "Cupón")

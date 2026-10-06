"""Esquemas de cada recurso de la API (ver reglas en services/validators.py)."""

USERS = {
    "name": {"type": "str", "required": True},
    "email": {"type": "email", "required": True, "unique": True},
    "role": {"type": "enum", "choices": ["admin", "user"], "default": "user"},
    "active": {"type": "bool", "default": True},
}

CATEGORIES = {
    "name": {"type": "str", "required": True, "unique": True},
    "description": {"type": "str", "max_len": 255, "default": ""},
}

SUPPLIERS = {
    "name": {"type": "str", "required": True},
    "email": {"type": "email", "required": True, "unique": True},
    "phone": {"type": "str", "max_len": 20, "default": ""},
}

PRODUCTS = {
    "name": {"type": "str", "required": True},
    "price": {"type": "number", "required": True, "min": 0},
    "stock": {"type": "int", "min": 0, "default": 0},
    "category_id": {"type": "int", "required": True, "ref": "categories"},
    "supplier_id": {"type": "int", "ref": "suppliers"},
}

CUSTOMERS = {
    "name": {"type": "str", "required": True},
    "email": {"type": "email", "required": True, "unique": True},
    "phone": {"type": "str", "max_len": 20, "default": ""},
}

ORDERS = {
    "customer_id": {"type": "int", "required": True, "ref": "customers"},
    "product_id": {"type": "int", "required": True, "ref": "products"},
    "quantity": {"type": "int", "required": True, "min": 1},
    "status": {
        "type": "enum",
        "choices": ["pending", "paid", "shipped", "cancelled"],
        "default": "pending",
    },
}

DEPARTMENTS = {
    "name": {"type": "str", "required": True, "unique": True},
}

EMPLOYEES = {
    "name": {"type": "str", "required": True},
    "email": {"type": "email", "required": True, "unique": True},
    "department_id": {"type": "int", "required": True, "ref": "departments"},
    "salary": {"type": "number", "required": True, "min": 0},
}

REVIEWS = {
    "product_id": {"type": "int", "required": True, "ref": "products"},
    "customer_id": {"type": "int", "required": True, "ref": "customers"},
    "rating": {"type": "int", "required": True, "min": 1, "max": 5},
    "comment": {"type": "str", "max_len": 500, "default": ""},
}

COUPONS = {
    "code": {"type": "str", "required": True, "unique": True, "transform": "upper", "max_len": 30},
    "discount": {"type": "number", "required": True, "min": 1, "max": 100},
    "active": {"type": "bool", "default": True},
}

ALL = {
    "users": USERS,
    "categories": CATEGORIES,
    "suppliers": SUPPLIERS,
    "products": PRODUCTS,
    "customers": CUSTOMERS,
    "orders": ORDERS,
    "departments": DEPARTMENTS,
    "employees": EMPLOYEES,
    "reviews": REVIEWS,
    "coupons": COUPONS,
}

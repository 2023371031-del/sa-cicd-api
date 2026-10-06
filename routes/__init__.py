from routes.categories import categories_bp
from routes.coupons import coupons_bp
from routes.customers import customers_bp
from routes.departments import departments_bp
from routes.employees import employees_bp
from routes.orders import orders_bp
from routes.products import products_bp
from routes.reviews import reviews_bp
from routes.suppliers import suppliers_bp
from routes.system import system_bp
from routes.users import users_bp

ALL_BLUEPRINTS = [
    system_bp,
    users_bp,
    categories_bp,
    suppliers_bp,
    products_bp,
    customers_bp,
    orders_bp,
    departments_bp,
    employees_bp,
    reviews_bp,
    coupons_bp,
]

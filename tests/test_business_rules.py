"""Pruebas de reglas de negocio, filtros y endpoints especiales."""


# ---------- Unicidad e integridad referencial ----------

def test_duplicate_email_conflict(client):
    res = client.post("/api/users", json={"name": "Otra Ana", "email": "ANA@mail.com"})
    assert res.status_code == 409


def test_patch_keeps_own_unique_value(client):
    res = client.patch("/api/users/1", json={"email": "ana@mail.com"})
    assert res.status_code == 200


def test_patch_duplicate_unique_value(client):
    res = client.patch("/api/users/2", json={"email": "ana@mail.com"})
    assert res.status_code == 409


def test_foreign_key_must_exist(client):
    res = client.post("/api/products", json={"name": "X", "price": 1, "category_id": 999})
    assert res.status_code == 400
    assert "no existe" in res.get_json()["error"]


def test_cannot_delete_referenced_record(client):
    res = client.delete("/api/categories/1")
    assert res.status_code == 409


def test_email_is_normalized(client):
    res = client.post("/api/users", json={"name": "  Beto ", "email": " BETO@Mail.com "})
    data = res.get_json()["data"]
    assert data["name"] == "Beto"
    assert data["email"] == "beto@mail.com"
    assert data["role"] == "user" and data["active"] is True


def test_coupon_code_is_uppercase(client):
    data = client.post("/api/coupons", json={"code": "promo", "discount": 5}).get_json()["data"]
    assert data["code"] == "PROMO"


# ---------- Validaciones ----------

def test_invalid_json_body(client):
    res = client.post("/api/users", data="{malo", content_type="application/json")
    assert res.status_code == 400


def test_body_must_be_object(client):
    res = client.post("/api/users", json=[1, 2])
    assert res.status_code == 400


def test_bool_field_type(client):
    assert client.patch("/api/users/1", json={"active": "si"}).status_code == 400


def test_enum_field(client):
    assert client.patch("/api/users/1", json={"role": "root"}).status_code == 400


def test_int_field_rejects_float(client):
    assert client.patch("/api/products/1", json={"stock": 1.5}).status_code == 400


def test_number_rejects_bool(client):
    assert client.patch("/api/products/1", json={"price": True}).status_code == 400


def test_text_too_long(client):
    assert client.patch("/api/users/1", json={"name": "a" * 101}).status_code == 400


def test_empty_text(client):
    assert client.patch("/api/users/1", json={"name": "   "}).status_code == 400


def test_put_requires_all_fields(client):
    res = client.put("/api/users/1", json={"name": "Solo nombre"})
    assert res.status_code == 400
    assert "obligatorio" in res.get_json()["error"]


# ---------- Listados: filtros, búsqueda, orden y paginación ----------

def test_filter_by_field(client):
    data = client.get("/api/products?category_id=1").get_json()["data"]
    assert data and all(p["category_id"] == 1 for p in data)


def test_search(client):
    data = client.get("/api/users?q=luis").get_json()["data"]
    assert [u["id"] for u in data] == [2]


def test_sort_desc_and_limit(client):
    data = client.get("/api/products?sort=-price&limit=2").get_json()["data"]
    assert len(data) == 2 and data[0]["price"] >= data[1]["price"]


def test_offset(client):
    data = client.get("/api/products?offset=3").get_json()["data"]
    assert [p["id"] for p in data] == [4]


def test_sort_invalid_field(client):
    assert client.get("/api/products?sort=password").status_code == 400


def test_limit_invalid(client):
    assert client.get("/api/products?limit=abc").status_code == 400


# ---------- Pedidos ----------

def test_order_total_is_calculated(client):
    res = client.post("/api/orders", json={"customer_id": 1, "product_id": 2, "quantity": 2})
    data = res.get_json()["data"]
    assert data["total"] == 45.0
    assert data["status"] == "pending"


def test_order_total_recalculated_on_patch(client):
    data = client.patch("/api/orders/1", json={"quantity": 5}).get_json()["data"]
    assert data["total"] == 75.0


def test_cancel_order(client):
    res = client.post("/api/orders/2/cancel")
    assert res.status_code == 200
    assert res.get_json()["data"]["status"] == "cancelled"


def test_cannot_cancel_twice(client):
    client.post("/api/orders/2/cancel")
    assert client.post("/api/orders/2/cancel").status_code == 409


def test_cancel_order_not_found(client):
    assert client.post("/api/orders/999/cancel").status_code == 404


# ---------- Endpoints anidados y especiales ----------

def test_category_products(client):
    data = client.get("/api/categories/1/products").get_json()["data"]
    assert {p["id"] for p in data} == {1, 2}


def test_category_products_not_found(client):
    assert client.get("/api/categories/999/products").status_code == 404


def test_supplier_products(client):
    data = client.get("/api/suppliers/2/products").get_json()["data"]
    assert {p["id"] for p in data} == {3, 4}


def test_customer_orders(client):
    data = client.get("/api/customers/1/orders").get_json()["data"]
    assert [o["id"] for o in data] == [1]


def test_department_employees(client):
    data = client.get("/api/departments/2/employees").get_json()["data"]
    assert [e["id"] for e in data] == [2]


def test_product_reviews(client):
    data = client.get("/api/products/1/reviews").get_json()["data"]
    assert [r["id"] for r in data] == [1]


def test_product_rating(client):
    data = client.get("/api/products/1/rating").get_json()["data"]
    assert data == {"product_id": 1, "reviews": 1, "average": 5.0}


def test_product_rating_without_reviews(client):
    data = client.get("/api/products/2/rating").get_json()["data"]
    assert data["average"] is None


def test_low_stock_default(client):
    data = client.get("/api/products/low-stock").get_json()["data"]
    assert {p["id"] for p in data} == {2, 4}


def test_low_stock_threshold(client):
    data = client.get("/api/products/low-stock?threshold=5").get_json()["data"]
    assert [p["id"] for p in data] == [4]


def test_low_stock_invalid_threshold(client):
    assert client.get("/api/products/low-stock?threshold=-1").status_code == 400


def test_toggle_user_active(client):
    data = client.post("/api/users/3/toggle-active").get_json()["data"]
    assert data["active"] is True


def test_validate_coupon_active(client):
    res = client.post("/api/coupons/validate", json={"code": "bienvenida10"})
    assert res.get_json()["data"] == {"code": "BIENVENIDA10", "valid": True, "discount": 10}


def test_validate_coupon_inactive(client):
    data = client.post("/api/coupons/validate", json={"code": "VERANO25"}).get_json()["data"]
    assert data["valid"] is False


def test_validate_coupon_not_found(client):
    assert client.post("/api/coupons/validate", json={"code": "NOEXISTE"}).status_code == 404


def test_validate_coupon_missing_code(client):
    assert client.post("/api/coupons/validate", json={}).status_code == 400

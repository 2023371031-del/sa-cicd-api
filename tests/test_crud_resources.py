"""Pruebas de los 6 endpoints CRUD de los 10 recursos (60 endpoints)."""
import pytest

# recurso -> (cuerpo válido para POST/PUT, cambio parcial para PATCH, cuerpo inválido)
CASES = {
    "users": (
        {"name": "Pedro", "email": "pedro@mail.com"},
        {"role": "admin"},
        {"name": "Pedro", "email": "no-es-email"},
    ),
    "categories": (
        {"name": "Lácteos", "description": "Leche y quesos"},
        {"description": "Solo leche"},
        {"name": ""},
    ),
    "suppliers": (
        {"name": "Proveedor X", "email": "x@prov.com", "phone": "123"},
        {"phone": "999"},
        {"name": "Proveedor X"},
    ),
    "products": (
        {"name": "Jugo", "price": 20, "stock": 5, "category_id": 1, "supplier_id": 1},
        {"stock": 50},
        {"name": "Jugo", "price": -1, "category_id": 1},
    ),
    "customers": (
        {"name": "Elena", "email": "elena@mail.com"},
        {"phone": "4420000000"},
        {"name": 123, "email": "elena@mail.com"},
    ),
    "orders": (
        {"customer_id": 1, "product_id": 2, "quantity": 4},
        {"status": "shipped"},
        {"customer_id": 1, "product_id": 2, "quantity": 0},
    ),
    "departments": (
        {"name": "Recursos Humanos"},
        {"name": "RH"},
        {"name": None},
    ),
    "employees": (
        {"name": "Raúl", "email": "raul@empresa.com", "department_id": 1, "salary": 9000},
        {"salary": 9500.5},
        {"name": "Raúl", "email": "raul@empresa.com", "department_id": 1, "salary": "mucho"},
    ),
    "reviews": (
        {"product_id": 2, "customer_id": 1, "rating": 4, "comment": "Bien"},
        {"rating": 2},
        {"product_id": 2, "customer_id": 1, "rating": 6},
    ),
    "coupons": (
        {"code": "nuevo50", "discount": 50},
        {"active": False},
        {"code": "X", "discount": 0},
    ),
}

RESOURCES = list(CASES)


@pytest.mark.parametrize("resource", RESOURCES)
def test_list(client, resource):
    res = client.get(f"/api/{resource}")
    body = res.get_json()
    assert res.status_code == 200
    assert body["statusCode"] == 200
    assert isinstance(body["data"], list) and len(body["data"]) >= 2


@pytest.mark.parametrize("resource", RESOURCES)
def test_get_one(client, resource):
    res = client.get(f"/api/{resource}/1")
    assert res.status_code == 200
    assert res.get_json()["data"]["id"] == 1


@pytest.mark.parametrize("resource", RESOURCES)
def test_get_not_found(client, resource):
    res = client.get(f"/api/{resource}/999")
    assert res.status_code == 404
    assert "no encontrad" in res.get_json()["error"]


@pytest.mark.parametrize("resource", RESOURCES)
def test_create(client, resource):
    valid, _, _ = CASES[resource]
    res = client.post(f"/api/{resource}", json=valid)
    assert res.status_code == 201
    created = res.get_json()["data"]
    assert created["id"] > 0
    assert client.get(f"/api/{resource}/{created['id']}").status_code == 200


@pytest.mark.parametrize("resource", RESOURCES)
def test_create_invalid(client, resource):
    _, _, invalid = CASES[resource]
    res = client.post(f"/api/{resource}", json=invalid)
    assert res.status_code == 400
    assert res.get_json()["statusCode"] == 400


@pytest.mark.parametrize("resource", RESOURCES)
def test_create_without_json(client, resource):
    res = client.post(f"/api/{resource}", data="texto", content_type="text/plain")
    assert res.status_code == 415


@pytest.mark.parametrize("resource", RESOURCES)
def test_create_extra_field(client, resource):
    valid, _, _ = CASES[resource]
    res = client.post(f"/api/{resource}", json={**valid, "hacker": True})
    assert res.status_code == 400
    assert "no permitidos" in res.get_json()["error"]


@pytest.mark.parametrize("resource", RESOURCES)
def test_replace(client, resource):
    valid, _, _ = CASES[resource]
    res = client.put(f"/api/{resource}/2", json=valid)
    assert res.status_code == 200
    assert res.get_json()["data"]["id"] == 2


@pytest.mark.parametrize("resource", RESOURCES)
def test_replace_not_found(client, resource):
    valid, _, _ = CASES[resource]
    assert client.put(f"/api/{resource}/999", json=valid).status_code == 404


@pytest.mark.parametrize("resource", RESOURCES)
def test_patch(client, resource):
    _, partial, _ = CASES[resource]
    res = client.patch(f"/api/{resource}/2", json=partial)
    assert res.status_code == 200
    data = res.get_json()["data"]
    for key, value in partial.items():
        assert data[key] == value


@pytest.mark.parametrize("resource", RESOURCES)
def test_patch_empty(client, resource):
    res = client.patch(f"/api/{resource}/1", json={})
    assert res.status_code == 400


@pytest.mark.parametrize("resource", RESOURCES)
def test_delete(client, resource):
    valid, _, _ = CASES[resource]
    new_id = client.post(f"/api/{resource}", json=valid).get_json()["data"]["id"]
    res = client.delete(f"/api/{resource}/{new_id}")
    assert res.status_code == 200
    assert client.get(f"/api/{resource}/{new_id}").status_code == 404


@pytest.mark.parametrize("resource", RESOURCES)
def test_delete_not_found(client, resource):
    assert client.delete(f"/api/{resource}/999").status_code == 404

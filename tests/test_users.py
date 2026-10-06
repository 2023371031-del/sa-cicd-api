"""Pruebas de los 5 endpoints de usuarios."""
import pytest

NEW_USER = {"name": "Pedro", "email": "pedro@mail.com"}


# ---------- 1. GET /api/users ----------

def test_list_users(client):
    res = client.get("/api/users")
    body = res.get_json()
    assert res.status_code == 200
    assert body["statusCode"] == 200
    assert [u["id"] for u in body["data"]] == [1, 2, 3]


# ---------- 2. GET /api/users/<id> ----------

def test_get_user(client):
    res = client.get("/api/users/1")
    assert res.status_code == 200
    assert res.get_json()["data"]["email"] == "ana@mail.com"


def test_get_user_not_found(client):
    res = client.get("/api/users/999")
    assert res.status_code == 404
    assert res.get_json() == {"statusCode": 404, "error": "Usuario no encontrado"}


def test_get_user_invalid_id(client):
    assert client.get("/api/users/abc").status_code == 404


# ---------- 3. POST /api/users ----------

def test_create_user(client):
    res = client.post("/api/users", json=NEW_USER)
    assert res.status_code == 201
    data = res.get_json()["data"]
    assert data == {"id": 4, "name": "Pedro", "email": "pedro@mail.com", "role": "user", "active": True}
    assert client.get("/api/users/4").status_code == 200


def test_create_user_normalizes_data(client):
    data = client.post("/api/users", json={"name": "  Beto ", "email": " BETO@Mail.com "}).get_json()["data"]
    assert data["name"] == "Beto"
    assert data["email"] == "beto@mail.com"


def test_create_user_duplicate_email(client):
    res = client.post("/api/users", json={"name": "Otra Ana", "email": "ANA@mail.com"})
    assert res.status_code == 409


@pytest.mark.parametrize("body, message", [
    ({"email": "x@mail.com"}, "obligatorio"),
    ({"name": "X"}, "obligatorio"),
    ({"name": "   ", "email": "x@mail.com"}, "vacío"),
    ({"name": 123, "email": "x@mail.com"}, "texto"),
    ({"name": "a" * 101, "email": "x@mail.com"}, "más de 100"),
    ({"name": "X", "email": "no-es-email"}, "email válido"),
    ({"name": "X", "email": "x@mail.com", "role": "root"}, "uno de"),
    ({"name": "X", "email": "x@mail.com", "active": "si"}, "true o false"),
    ({"name": "X", "email": "x@mail.com", "id": 50}, "no permitidos"),
])
def test_create_user_invalid(client, body, message):
    res = client.post("/api/users", json=body)
    assert res.status_code == 400
    assert message in res.get_json()["error"]


def test_create_user_without_json(client):
    res = client.post("/api/users", data="texto", content_type="text/plain")
    assert res.status_code == 415


def test_create_user_malformed_json(client):
    res = client.post("/api/users", data="{malo", content_type="application/json")
    assert res.status_code == 400


def test_create_user_body_not_object(client):
    assert client.post("/api/users", json=[1, 2]).status_code == 400


# ---------- 4. PUT /api/users/<id> ----------

def test_update_user(client):
    res = client.put("/api/users/2", json={"name": "Luis P.", "role": "admin"})
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["name"] == "Luis P." and data["role"] == "admin"
    assert data["email"] == "luis@mail.com"


def test_update_user_keeps_own_email(client):
    assert client.put("/api/users/1", json={"email": "ana@mail.com"}).status_code == 200


def test_update_user_duplicate_email(client):
    assert client.put("/api/users/2", json={"email": "ana@mail.com"}).status_code == 409


def test_update_user_empty_body(client):
    assert client.put("/api/users/1", json={}).status_code == 400


def test_update_user_invalid(client):
    assert client.put("/api/users/1", json={"active": "no"}).status_code == 400


def test_update_user_not_found(client):
    assert client.put("/api/users/999", json={"name": "X"}).status_code == 404


# ---------- 5. DELETE /api/users/<id> ----------

def test_delete_user(client):
    res = client.delete("/api/users/3")
    assert res.status_code == 200
    assert res.get_json()["data"] == {"message": "Usuario eliminado", "id": 3}
    assert client.get("/api/users/3").status_code == 404


def test_delete_user_not_found(client):
    assert client.delete("/api/users/999").status_code == 404


def test_delete_all_not_allowed(client):
    assert client.delete("/api/users").status_code == 405

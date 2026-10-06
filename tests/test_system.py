"""Pruebas de los endpoints de sistema y del manejo de errores."""
import config


def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json()["data"]["status"] == "ok"


def test_version(client, monkeypatch):
    monkeypatch.setenv("GIT_SHA", "abc123")
    data = client.get("/api/version").get_json()["data"]
    assert data == {"version": config.VERSION, "message": config.MESSAGE, "commit": "abc123"}


def test_endpoints_lists_at_least_60(client):
    data = client.get("/api/endpoints").get_json()["data"]
    assert data["total"] >= 60
    assert {"method": "GET", "path": "/api/health"} in data["endpoints"]


def test_stats(client):
    data = client.get("/api/stats").get_json()["data"]
    assert data["users"] == 3 and data["products"] == 4


def test_reset(client):
    client.delete("/api/coupons/2")
    assert client.post("/api/admin/reset").status_code == 200
    assert client.get("/api/coupons/2").status_code == 200


def test_route_not_found(client):
    res = client.get("/api/no-existe")
    assert res.status_code == 404
    assert res.get_json() == {"statusCode": 404, "error": "Ruta no encontrada"}


def test_method_not_allowed(client):
    assert client.delete("/api/users").status_code == 405


def test_internal_error_handler(client, monkeypatch):
    from services import user_service

    def boom(**_):
        raise RuntimeError("falla simulada")

    monkeypatch.setattr(user_service, "list", boom)
    client.application.config["PROPAGATE_EXCEPTIONS"] = False
    res = client.get("/api/users")
    assert res.status_code == 500
    assert res.get_json()["statusCode"] == 500

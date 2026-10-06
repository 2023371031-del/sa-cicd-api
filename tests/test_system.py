"""Pruebas del endpoint de health y del manejo de errores."""
import config


def test_health(client, monkeypatch):
    monkeypatch.setenv("GIT_SHA", "abc123")
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json()["data"] == {
        "status": "ok",
        "version": config.VERSION,
        "message": config.MESSAGE,
        "commit": "abc123",
    }


def test_route_not_found(client):
    res = client.get("/api/no-existe")
    assert res.status_code == 404
    assert res.get_json() == {"statusCode": 404, "error": "Ruta no encontrada"}


def test_internal_error_handler(client, monkeypatch):
    from services import user_service

    def boom():
        raise RuntimeError("falla simulada")

    monkeypatch.setattr(user_service, "get_all", boom)
    client.application.config["PROPAGATE_EXCEPTIONS"] = False
    res = client.get("/api/users")
    assert res.status_code == 500
    assert res.get_json()["statusCode"] == 500

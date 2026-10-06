"""Formato estándar de respuesta: {"statusCode": <código>, "data": ...} o {"statusCode", "error"}."""
from flask import jsonify, request

from services.user_service import ServiceError


def ok(data, status=200):
    return jsonify({"statusCode": status, "data": data}), status


def fail(message, status):
    return jsonify({"statusCode": status, "error": message}), status


def read_json():
    """Regresa el cuerpo JSON o lanza ServiceError (415 si no es JSON, 400 si está mal formado)."""
    if not request.is_json:
        raise ServiceError("El Content-Type debe ser application/json", 415)
    data = request.get_json(silent=True)
    if data is None:
        raise ServiceError("El cuerpo no es un JSON válido", 400)
    return data

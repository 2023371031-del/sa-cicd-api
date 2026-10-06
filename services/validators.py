"""Validación de cuerpos JSON contra un esquema de campos.

Un esquema es un diccionario {campo: reglas}. Reglas soportadas:
    type     -> "str", "email", "bool" o "enum"
    required -> el campo es obligatorio al crear
    default  -> valor por omisión si no se manda al crear
    max_len  -> longitud máxima para texto (100 por omisión)
    choices  -> valores permitidos para "enum"
"""
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _check_value(field, rules, value):
    kind = rules["type"]

    if kind in ("str", "email"):
        if not isinstance(value, str):
            return f"El campo '{field}' debe ser texto"
        value = value.strip()
        if not value:
            return f"El campo '{field}' no puede estar vacío"
        if len(value) > rules.get("max_len", 100):
            return f"El campo '{field}' no puede tener más de {rules.get('max_len', 100)} caracteres"
        if kind == "email" and not EMAIL_RE.match(value):
            return f"El campo '{field}' no tiene un formato de email válido"
        return None

    if kind == "bool":
        if not isinstance(value, bool):
            return f"El campo '{field}' debe ser true o false"
        return None

    # enum
    if value not in rules["choices"]:
        return f"El campo '{field}' debe ser uno de: {', '.join(rules['choices'])}"
    return None


def _normalize(rules, value):
    if isinstance(value, str):
        value = value.strip()
        if rules["type"] == "email":
            value = value.lower()
    return value


def validate(schema, data, partial=False):
    """Regresa (datos_limpios, None) o (None, mensaje_de_error).

    partial=True se usa en PUT: solo se validan los campos enviados.
    """
    if not isinstance(data, dict):
        return None, "El cuerpo debe ser un objeto JSON"

    extra = sorted(set(data) - set(schema))
    if extra:
        return None, f"Campos no permitidos: {', '.join(extra)}"

    if partial and not data:
        return None, "No se enviaron datos"

    clean = {}
    for field, rules in schema.items():
        if field not in data or data[field] is None:
            if partial:
                continue
            if rules.get("required"):
                return None, f"El campo '{field}' es obligatorio"
            clean[field] = rules.get("default")
            continue
        msg = _check_value(field, rules, data[field])
        if msg:
            return None, msg
        clean[field] = _normalize(rules, data[field])
    return clean, None

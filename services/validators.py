"""Validación genérica de cuerpos JSON contra un esquema de campos.

Un esquema es un diccionario {campo: reglas}. Reglas soportadas:
    type      -> "str", "email", "int", "number", "bool" o "enum"
    required  -> el campo es obligatorio al crear / reemplazar (PUT)
    default   -> valor por omisión si no se manda al crear
    min, max  -> límites para números
    max_len   -> longitud máxima para texto
    choices   -> valores permitidos para "enum"
    unique    -> no puede repetirse en la tabla (lo revisa el servicio)
    ref       -> llave foránea: nombre de la tabla a la que apunta (lo revisa el servicio)
    transform -> "lower" o "upper" para normalizar texto
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

    if kind == "enum":
        if value not in rules["choices"]:
            return f"El campo '{field}' debe ser uno de: {', '.join(rules['choices'])}"
        return None

    # int / number (bool es subclase de int en Python, por eso se excluye)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return f"El campo '{field}' debe ser numérico"
    if kind == "int" and not isinstance(value, int):
        return f"El campo '{field}' debe ser un número entero"
    if "min" in rules and value < rules["min"]:
        return f"El campo '{field}' debe ser mayor o igual a {rules['min']}"
    if "max" in rules and value > rules["max"]:
        return f"El campo '{field}' debe ser menor o igual a {rules['max']}"
    return None


def _normalize(rules, value):
    if isinstance(value, str):
        value = value.strip()
        if rules.get("transform") == "lower" or rules["type"] == "email":
            value = value.lower()
        elif rules.get("transform") == "upper":
            value = value.upper()
    return value


def validate(schema, data, partial=False):
    """Regresa (datos_limpios, None) o (None, mensaje_de_error).

    partial=True se usa en PATCH: solo se validan los campos enviados.
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

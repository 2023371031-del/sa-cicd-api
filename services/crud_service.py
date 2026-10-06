"""Servicio CRUD genérico: la lógica de negocio común a todos los recursos.

Las rutas nunca tocan la base de datos directamente; siempre pasan por aquí.
Los errores de negocio se lanzan como ServiceError(mensaje, código_http).
"""
from data import store
from services import schemas
from services.validators import validate


class ServiceError(Exception):
    def __init__(self, message, status):
        super().__init__(message)
        self.message = message
        self.status = status


class CrudService:
    def __init__(self, name, schema, label, before_save=None):
        self.name = name
        self.schema = schema
        self.label = label  # nombre en singular para los mensajes, ej. "Producto"
        self.before_save = before_save  # gancho opcional para campos calculados

    @property
    def rows(self):
        return store.table(self.name)

    # ---------------- Lectura ----------------

    def list(self, filters=None, q=None, sort=None, limit=None, offset=0):
        result = list(self.rows)
        for field, value in (filters or {}).items():
            result = [r for r in result if str(r.get(field)).lower() == str(value).lower()]
        if q:
            q = q.lower()
            result = [r for r in result if any(q in str(v).lower() for v in r.values())]
        if sort:
            desc = sort.startswith("-")
            key = sort.lstrip("-")
            if key not in self.schema and key != "id":
                raise ServiceError(f"No se puede ordenar por '{key}'", 400)
            result.sort(key=lambda r: (r.get(key) is None, r.get(key)), reverse=desc)
        if offset:
            result = result[offset:]
        if limit is not None:
            result = result[:limit]
        return result

    def get(self, item_id):
        item = next((r for r in self.rows if r["id"] == item_id), None)
        if item is None:
            raise ServiceError(f"{self.label} no encontrado", 404)
        return item

    def count(self):
        return len(self.rows)

    # ---------------- Escritura ----------------

    def create(self, data):
        clean = self._validated(data, partial=False)
        with store.lock:
            self._check_integrity(clean)
            item = {"id": store.next_id(self.name), **clean}
            if self.before_save:
                self.before_save(item)
            self.rows.append(item)
        return item

    def replace(self, item_id, data):
        self.get(item_id)
        clean = self._validated(data, partial=False)
        return self._apply(item_id, clean)

    def patch(self, item_id, data):
        self.get(item_id)
        clean = self._validated(data, partial=True)
        return self._apply(item_id, clean)

    def delete(self, item_id):
        with store.lock:
            item = self.get(item_id)
            self._check_not_referenced(item_id)
            self.rows.remove(item)
        return item

    # ---------------- Internos ----------------

    def _validated(self, data, partial):
        clean, msg = validate(self.schema, data, partial=partial)
        if msg:
            raise ServiceError(msg, 400)
        return clean

    def _apply(self, item_id, clean):
        with store.lock:
            self._check_integrity(clean, exclude_id=item_id)
            item = self.get(item_id)
            item.update(clean)
            if self.before_save:
                self.before_save(item)
        return item

    def _check_integrity(self, clean, exclude_id=None):
        for field, rules in self.schema.items():
            value = clean.get(field)
            if value is None:
                continue
            if rules.get("unique"):
                for r in self.rows:
                    if r["id"] != exclude_id and str(r.get(field)).lower() == str(value).lower():
                        raise ServiceError(f"Ya existe un registro con ese '{field}'", 409)
            if rules.get("ref"):
                if not any(r["id"] == value for r in store.table(rules["ref"])):
                    raise ServiceError(f"El '{field}' {value} no existe", 400)

    def _check_not_referenced(self, item_id):
        """No se permite borrar un registro si otro recurso apunta a él."""
        for table_name, schema in schemas.ALL.items():
            for field, rules in schema.items():
                if rules.get("ref") == self.name and any(
                    r.get(field) == item_id for r in store.table(table_name)
                ):
                    raise ServiceError(
                        f"No se puede eliminar: hay registros en '{table_name}' que lo usan", 409
                    )

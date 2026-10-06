import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from data import store  # noqa: E402


@pytest.fixture
def client():
    """Cliente de pruebas con los datos iniciales recargados en cada prueba."""
    store.reset()
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()

"""
Configuración global de tests.

Asegura que el almacenamiento en memoria se limpia
antes y después de CADA test, independientemente del archivo.
Esto evita que los datos de un test se filtren a otro.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.storage import reset_storage
from app.services.auth_service import reset_auth_service


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def clean_storage():
    """Limpia el almacenamiento antes y después de cada test."""
    reset_storage()
    reset_auth_service()
    yield
    reset_storage()
    reset_auth_service()


@pytest.fixture
async def client():
    """Cliente HTTP para tests — simula peticiones al servidor."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

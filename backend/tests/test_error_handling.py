"""
Pruebas para el manejo de errores de OddsEngine.
Los fixtures (client, clean_storage) están en conftest.py.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_404_returns_structured_error(client: AsyncClient):
    """Un partido inexistente devuelve error con formato estandarizado."""
    response = await client.get("/api/matches/no_existe_xyz")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "type" in data["error"]
    assert "message" in data["error"]
    assert "status_code" in data["error"]
    assert "timestamp" in data["error"]
    assert data["error"]["status_code"] == 404
    assert data["error"]["type"] == "NotFoundException"


@pytest.mark.anyio
async def test_404_message_includes_resource_id(client: AsyncClient):
    """El mensaje de error incluye el ID del recurso buscado."""
    response = await client.get("/api/matches/match_999")
    data = response.json()
    assert "match_999" in data["error"]["message"]


@pytest.mark.anyio
async def test_invalid_status_filter_returns_422(client: AsyncClient):
    """Un valor inválido en el filtro de status devuelve error 422."""
    response = await client.get("/api/matches", params={"status": "invalido"})
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["status_code"] == 422


@pytest.mark.anyio
async def test_health_still_works_after_errors(client: AsyncClient):
    """El health check sigue funcionando después de errores."""
    await client.get("/api/matches/no_existe")
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.anyio
async def test_valid_request_after_error(client: AsyncClient):
    """Las peticiones válidas funcionan después de un error."""
    await client.get("/api/matches/no_existe")
    response = await client.get("/api/matches")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.anyio
async def test_unknown_route_returns_404(client: AsyncClient):
    """Una ruta que no existe devuelve 404."""
    response = await client.get("/api/ruta_inventada")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_error_response_has_consistent_structure(client: AsyncClient):
    """Todos los errores tienen la misma estructura base."""
    r1 = await client.get("/api/matches/no_existe")
    r2 = await client.get("/api/matches", params={"status": "malo"})
    for r in [r1, r2]:
        data = r.json()
        assert "error" in data
        error = data["error"]
        assert all(key in error for key in ["type", "message", "status_code", "timestamp"])

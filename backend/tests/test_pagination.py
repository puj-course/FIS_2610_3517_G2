"""Tests de paginación (Sprint 12)."""
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_matches_default_pagination(client: AsyncClient):
    """Sin params explícitos, retorna hasta 10 partidos (default)."""
    response = await client.get("/api/matches")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10

@pytest.mark.anyio
async def test_matches_with_limit(client: AsyncClient):
    """limit=3 retorna como máximo 3 partidos."""
    response = await client.get("/api/matches?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3

@pytest.mark.anyio
async def test_matches_with_page(client: AsyncClient):
    """page=1&limit=3 retorna exactamente 3 partidos (hay 8 mock)."""
    response = await client.get("/api/matches?page=1&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3

@pytest.mark.anyio
async def test_matches_page_beyond_range(client: AsyncClient):
    """Página fuera de rango retorna lista vacía."""
    response = await client.get("/api/matches?page=999&limit=3")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.anyio
async def test_matches_invalid_limit(client: AsyncClient):
    """limit negativo retorna 422 (validación)."""
    response = await client.get("/api/matches?limit=-1")
    assert response.status_code == 422

@pytest.mark.anyio
async def test_matches_limit_zero(client: AsyncClient):
    """limit=0 retorna 422 (validación)."""
    response = await client.get("/api/matches?limit=0")
    assert response.status_code == 422

@pytest.mark.anyio
async def test_matches_invalid_page(client: AsyncClient):
    """page negativa retorna 422 (validación)."""
    response = await client.get("/api/matches?page=-1")
    assert response.status_code == 422

@pytest.mark.anyio
async def test_matches_page_zero(client: AsyncClient):
    """page=0 retorna 422 (validación)."""
    response = await client.get("/api/matches?page=0")
    assert response.status_code == 422

@pytest.mark.anyio
async def test_matches_second_page(client: AsyncClient):
    """Segunda página retorna partidos distintos a la primera."""
    resp1 = await client.get("/api/matches?page=1&limit=3")
    resp2 = await client.get("/api/matches?page=2&limit=3")
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    ids1 = [m["id"] for m in resp1.json()]
    ids2 = [m["id"] for m in resp2.json()]
    # No debe haber overlap entre páginas
    assert not set(ids1) & set(ids2)

@pytest.mark.anyio
async def test_matches_pagination_with_filter(client: AsyncClient):
    """Paginación se aplica después de filtros."""
    response = await client.get("/api/matches?status=upcoming&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2
    for match in data:
        assert match["status"] == "upcoming"

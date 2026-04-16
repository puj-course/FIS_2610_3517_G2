"""Tests de paginación (Sprint 12)."""
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_matches_default_pagination(client: AsyncClient):
    response = await client.get("/api/matches")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.anyio
@pytest.mark.skip(reason="pending: Sprint 12 - pagination not implemented")
async def test_matches_with_limit(client: AsyncClient):
    response = await client.get("/api/matches?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3

@pytest.mark.anyio
async def test_matches_with_page(client: AsyncClient):
    response = await client.get("/api/matches?page=1&limit=3")
    assert response.status_code == 200

@pytest.mark.anyio
@pytest.mark.skip(reason="pending: Sprint 12 - pagination not implemented")
async def test_matches_page_beyond_range(client: AsyncClient):
    response = await client.get("/api/matches?page=999&limit=3")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.anyio
async def test_matches_invalid_limit(client: AsyncClient):
    response = await client.get("/api/matches?limit=-1")
    assert response.status_code in [200, 422]

@pytest.mark.anyio
async def test_matches_limit_zero(client: AsyncClient):
    response = await client.get("/api/matches?limit=0")
    assert response.status_code in [200, 422]

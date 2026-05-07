"""Tests de health endpoints (Sprint 12)."""
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_health_basic(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "OddsEngine"

@pytest.mark.anyio
async def test_health_has_version(client: AsyncClient):
    response = await client.get("/health")
    data = response.json()
    assert "version" in data
    assert data["version"] == "1.0.0"

@pytest.mark.anyio
async def test_health_has_data_mode(client: AsyncClient):
    response = await client.get("/health")
    data = response.json()
    assert "data_mode" in data

@pytest.mark.anyio
async def test_health_detailed(client: AsyncClient):
    response = await client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data

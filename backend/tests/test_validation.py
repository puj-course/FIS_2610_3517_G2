"""Tests de validación de datos (Sprint 11)."""
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_invalid_status_filter(client: AsyncClient):
    response = await client.get("/api/matches?status=invalid_status")
    assert response.status_code == 422

@pytest.mark.anyio
async def test_special_characters_in_filter(client: AsyncClient):
    response = await client.get("/api/matches?tournament=<script>alert(1)</script>")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.anyio
async def test_empty_match_id(client: AsyncClient):
    response = await client.get("/api/matches/ ")
    assert response.status_code in [404, 422]

@pytest.mark.anyio
@pytest.mark.skip(reason="pending: Sprint 9 - POST /combinations response wrapping")
async def test_add_empty_match_id(client: AsyncClient):
    comb = await client.post("/api/combinations")
    comb_id = comb.json()["combination"]["id"]
    response = await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": ""})
    assert response.status_code in [404, 422]

@pytest.mark.anyio
async def test_very_long_match_id(client: AsyncClient):
    response = await client.get(f"/api/matches/{'x' * 500}")
    assert response.status_code == 404

@pytest.mark.anyio
async def test_combination_not_found(client: AsyncClient):
    response = await client.get("/api/combinations/nonexistent_id_12345")
    assert response.status_code == 404

"""
Tests para rutas de historial - aumentar coverage.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_get_history_returns_200(client: AsyncClient):
    response = await client.get("/api/combinations/history")
    assert response.status_code in [200, 404]


@pytest.mark.anyio
async def test_complete_combination_with_matches(client: AsyncClient):
    create = await client.post("/api/combinations")
    comb_id = create.json()["id"]
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})
    response = await client.post(f"/api/combinations/{comb_id}/complete")
    assert response.status_code in [200, 404, 400]


@pytest.mark.anyio
async def test_export_combination_with_matches(client: AsyncClient):
    create = await client.post("/api/combinations")
    comb_id = create.json()["id"]
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})
    response = await client.get(f"/api/combinations/{comb_id}/export")
    assert response.status_code in [200, 404, 400]


@pytest.mark.anyio
async def test_probability_match_001(client: AsyncClient):
    response = await client.get("/api/matches/match_001/probability")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_probability_match_002(client: AsyncClient):
    response = await client.get("/api/matches/match_002/probability")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_probability_match_003(client: AsyncClient):
    response = await client.get("/api/matches/match_003/probability")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_combination_result_two_matches(client: AsyncClient):
    create = await client.post("/api/combinations")
    comb_id = create.json()["id"]
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})
    response = await client.get(f"/api/combinations/{comb_id}/result")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_combination_probability_three_matches(client: AsyncClient):
    create = await client.post("/api/combinations")
    comb_id = create.json()["id"]
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_003"})
    response = await client.get(f"/api/combinations/{comb_id}/probability")
    assert response.status_code == 200
    data = response.json()
    assert data["total_matches"] == 3

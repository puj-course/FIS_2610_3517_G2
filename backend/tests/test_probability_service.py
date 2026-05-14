"""
Tests para el servicio de probabilidad - aumentar coverage.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_individual_probability_confidence(client: AsyncClient):
    response = await client.get("/api/matches/match_001/probability")
    data = response.json()
    assert "confidence" in data
    assert data["confidence"] in ["low", "medium", "high"]


@pytest.mark.anyio
async def test_individual_probability_message(client: AsyncClient):
    response = await client.get("/api/matches/match_001/probability")
    data = response.json()
    assert "message" in data
    assert len(data["message"]) > 0


@pytest.mark.anyio
async def test_individual_probability_factors(client: AsyncClient):
    response = await client.get("/api/matches/match_001/probability")
    data = response.json()
    assert "factors_home" in data
    assert "factors_away" in data


@pytest.mark.anyio
async def test_probability_nonexistent_match(client: AsyncClient):
    response = await client.get("/api/matches/nonexistent-match/probability")
    assert response.status_code in [404, 400]


@pytest.mark.anyio
async def test_combination_probability_with_one_match(client: AsyncClient):
    create = await client.post("/api/combinations")
    comb_id = create.json()["id"]
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})

    response = await client.get(f"/api/combinations/{comb_id}/probability")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.anyio
async def test_combination_result_has_all_fields(client: AsyncClient):
    create = await client.post("/api/combinations")
    comb_id = create.json()["id"]
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})

    response = await client.get(f"/api/combinations/{comb_id}/result")
    assert response.status_code == 200
    data = response.json()
    assert "combination_id" in data
    assert "probability" in data
    assert "risk_level" in data
    assert "matches" in data
    assert "total_matches" in data


@pytest.mark.anyio
async def test_risk_level_is_valid(client: AsyncClient):
    create = await client.post("/api/combinations")
    comb_id = create.json()["id"]
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})

    response = await client.get(f"/api/combinations/{comb_id}/probability")
    data = response.json()
    assert data["risk_level"] in ["low", "medium", "high"]


@pytest.mark.anyio
async def test_multiple_matches_probability_decreases(client: AsyncClient):
    create = await client.post("/api/combinations")
    comb_id = create.json()["id"]
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})

    resp_2 = await client.get(f"/api/combinations/{comb_id}/probability")
    prob_2 = resp_2.json()["total_probability"]

    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_003"})
    resp_3 = await client.get(f"/api/combinations/{comb_id}/probability")
    prob_3 = resp_3.json()["total_probability"]

    assert prob_3 <= prob_2

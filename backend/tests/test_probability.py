"""
Pruebas de probabilidad individual y combinada (Sprint 6-7).
"""

import pytest
from httpx import AsyncClient


# === PROBABILIDAD INDIVIDUAL (Sprint 6) ===

@pytest.mark.anyio
async def test_probability_returns_200(client: AsyncClient):
    response = await client.get("/api/matches/match_001/probability")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_probability_has_both_players(client: AsyncClient):
    response = await client.get("/api/matches/match_001/probability")
    data = response.json()
    assert "player_home_probability" in data
    assert "player_away_probability" in data
    assert data["player_home_name"] != ""
    assert data["player_away_name"] != ""


@pytest.mark.anyio
async def test_probability_sums_approximately_100(client: AsyncClient):
    response = await client.get("/api/matches/match_001/probability")
    data = response.json()
    total = data["player_home_probability"] + data["player_away_probability"]
    assert 99.5 <= total <= 100.5


@pytest.mark.anyio
async def test_probability_in_valid_range(client: AsyncClient):
    response = await client.get("/api/matches/match_001/probability")
    data = response.json()
    assert 0 <= data["player_home_probability"] <= 100
    assert 0 <= data["player_away_probability"] <= 100


@pytest.mark.anyio
async def test_probability_has_factors(client: AsyncClient):
    response = await client.get("/api/matches/match_001/probability")
    data = response.json()
    assert len(data["factors_home"]) == 3
    assert len(data["factors_away"]) == 3
    for f in data["factors_home"]:
        assert "name" in f
        assert "weight" in f
        assert "value" in f


@pytest.mark.anyio
async def test_probability_factors_weights_sum_1(client: AsyncClient):
    response = await client.get("/api/matches/match_001/probability")
    data = response.json()
    total_weight = sum(f["weight"] for f in data["factors_home"])
    assert abs(total_weight - 1.0) < 0.01


@pytest.mark.anyio
async def test_probability_has_confidence(client: AsyncClient):
    response = await client.get("/api/matches/match_001/probability")
    data = response.json()
    assert data["confidence"] in ["high", "medium", "low"]


@pytest.mark.anyio
async def test_probability_has_message(client: AsyncClient):
    response = await client.get("/api/matches/match_001/probability")
    data = response.json()
    assert len(data["message"]) > 0


@pytest.mark.anyio
async def test_probability_match_not_found(client: AsyncClient):
    response = await client.get("/api/matches/fake_match/probability")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_probability_coherence(client: AsyncClient):
    """Jugador con mejores stats debería tener mayor probabilidad."""
    response = await client.get("/api/matches/match_001/probability")
    data = response.json()
    # Al menos uno debe tener > 50%
    assert data["player_home_probability"] != data["player_away_probability"] or \
           data["confidence"] == "low"


# === PROBABILIDAD COMBINADA (Sprint 7) ===

@pytest.mark.anyio
async def test_combination_probability_needs_2_matches(client: AsyncClient):
    """Combinada con menos de 2 partidos da mensaje, no error."""
    # Crear combinada vacía
    create_resp = await client.post("/api/combinations")
    comb_id = create_resp.json()["combination"]["id"]

    # Agregar solo 1 partido
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})

    # Pedir probabilidad
    response = await client.get(f"/api/combinations/{comb_id}/probability")
    assert response.status_code == 200
    data = response.json()
    assert data["total_probability"] == 0
    assert "al menos 2" in data["message"].lower()


@pytest.mark.anyio
async def test_combination_probability_with_matches(client: AsyncClient):
    """Combinada con 2+ partidos calcula correctamente."""
    create_resp = await client.post("/api/combinations")
    comb_id = create_resp.json()["combination"]["id"

    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})

    response = await client.get(f"/api/combinations/{comb_id}/probability")
    assert response.status_code == 200
    data = response.json()
    assert data["total_probability"] > 0
    assert data["total_probability"] <= 100
    assert data["risk_level"] in ["low", "medium", "high"]
    assert len(data["matches_detail"]) == 2


@pytest.mark.anyio
async def test_combination_probability_multiplicative(client: AsyncClient):
    """Más partidos = menor probabilidad total (multiplicación)."""
    create_resp = await client.post("/api/combinations")
    comb_id = create_resp.json()["combination"]["id"]

    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})

    resp_2 = await client.get(f"/api/combinations/{comb_id}/probability")
    prob_2 = resp_2.json()["total_probability"]

    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_003"})

    resp_3 = await client.get(f"/api/combinations/{comb_id}/probability")
    prob_3 = resp_3.json()["total_probability"]

    # Con 3 partidos la probabilidad debería ser menor
    assert prob_3 < prob_2


@pytest.mark.anyio
async def test_combination_result_endpoint(client: AsyncClient):
    """GET /combinations/{id}/result retorna resultado completo."""
    create_resp = await client.post("/api/combinations")
    comb_id = create_resp.json()["combination"]["id"]

    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})

    response = await client.get(f"/api/combinations/{comb_id}/result")
    assert response.status_code == 200
    data = response.json()
    assert "probability" in data
    assert "risk_level" in data
    assert "matches" in data
    assert len(data["matches"]) == 2


@pytest.mark.anyio
async def test_combination_risk_classification(client: AsyncClient):
    """Verificar que risk_level es válido."""
    create_resp = await client.post("/api/combinations")
    comb_id = create_resp.json()["combination"]["id"]

    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})

    response = await client.get(f"/api/combinations/{comb_id}/probability")
    data = response.json()
    assert data["risk_level"] in ["low", "medium", "high"]
    assert len(data["message"]) > 0

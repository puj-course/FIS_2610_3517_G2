"""
Pruebas de integración para el flujo completo de HU-02.
Los fixtures (client, clean_storage) están en conftest.py.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_user_flow_browse_and_build_combination(client: AsyncClient):
    """Flujo: usuario ve partidos, crea combinada, agrega 3, quita 1, consulta."""
    r = await client.get("/api/matches")
    matches = r.json()
    assert len(matches) > 0

    r = await client.post("/api/combinations")
    assert r.status_code == 201
    comb_id = r.json()["id"]

    for i in range(3):
        r = await client.post(
            f"/api/combinations/{comb_id}/matches",
            json={"match_id": matches[i]["id"]},
        )
        assert r.status_code == 200

    r = await client.delete(f"/api/combinations/{comb_id}/matches/{matches[1]['id']}")
    assert r.status_code == 200

    r = await client.get(f"/api/combinations/{comb_id}")
    data = r.json()
    assert data["total_selections"] == 2
    match_ids = [s["match_id"] for s in data["selections"]]
    assert matches[0]["id"] in match_ids
    assert matches[2]["id"] in match_ids


@pytest.mark.anyio
async def test_user_flow_filter_then_add(client: AsyncClient):
    """Flujo: filtrar partidos por upcoming, luego agregar a combinada."""
    r = await client.get("/api/matches", params={"status": "upcoming"})
    upcoming = r.json()
    assert len(upcoming) > 0

    r = await client.post("/api/combinations")
    comb_id = r.json()["id"]

    r = await client.post(
        f"/api/combinations/{comb_id}/matches",
        json={"match_id": upcoming[0]["id"]},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["total_selections"] == 1


@pytest.mark.anyio
async def test_user_flow_empty_combination_then_delete(client: AsyncClient):
    """Flujo: crear combinada vacía y eliminarla."""
    r = await client.post("/api/combinations")
    comb_id = r.json()["id"]
    r = await client.delete(f"/api/combinations/{comb_id}")
    assert r.status_code == 200
    r = await client.get(f"/api/combinations/{comb_id}")
    assert r.status_code == 404


@pytest.mark.anyio
async def test_user_flow_multiple_combinations(client: AsyncClient):
    """Flujo: usuario crea dos combinadas diferentes con partidos distintos."""
    r = await client.get("/api/matches")
    matches = r.json()

    r1 = await client.post("/api/combinations")
    comb1_id = r1.json()["id"]
    await client.post(
        f"/api/combinations/{comb1_id}/matches",
        json={"match_id": matches[0]["id"]},
    )

    r2 = await client.post("/api/combinations")
    comb2_id = r2.json()["id"]
    await client.post(
        f"/api/combinations/{comb2_id}/matches",
        json={"match_id": matches[1]["id"]},
    )

    c1 = await client.get(f"/api/combinations/{comb1_id}")
    c2 = await client.get(f"/api/combinations/{comb2_id}")
    assert c1.json()["selections"][0]["match_id"] == matches[0]["id"]
    assert c2.json()["selections"][0]["match_id"] == matches[1]["id"]

    r = await client.get("/api/combinations")
    assert len(r.json()) == 2


@pytest.mark.anyio
async def test_selection_preserves_match_data(client: AsyncClient):
    """La selección preserva los datos del partido."""
    r = await client.get("/api/matches/match_001")
    match = r.json()

    r = await client.post("/api/combinations")
    comb_id = r.json()["id"]

    r = await client.post(
        f"/api/combinations/{comb_id}/matches",
        json={"match_id": "match_001"},
    )
    selection = r.json()["selections"][0]
    assert selection["player_home_name"] == match["player_home"]["name"]
    assert selection["player_away_name"] == match["player_away"]["name"]
    assert selection["tournament_name"] == match["tournament"]["name"]

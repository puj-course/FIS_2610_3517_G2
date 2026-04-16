"""
Pruebas de historial y exportar combinadas (Sprint 9).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_history_returns_list(client: AsyncClient):
    response = await client.get("/api/combinations/history")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "combinations" in data


@pytest.mark.anyio
async def test_complete_combination(client: AsyncClient):
    create_resp = await client.post("/api/combinations")
    comb_id = create_resp.json()["combination"]["id"]
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})

    response = await client.post(f"/api/combinations/{comb_id}/complete")
    assert response.status_code == 200
    data = response.json()
    assert "probability" in data
    assert "completed_at" in data


@pytest.mark.anyio
async def test_export_combination(client: AsyncClient):
    create_resp = await client.post("/api/combinations")
    comb_id = create_resp.json()["combination"]["id"]
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})

    response = await client.get(f"/api/combinations/{comb_id}/export")
    assert response.status_code == 200
    data = response.json()
    assert "export_info" in data
    assert "combination" in data
    assert "result" in data
    assert "matches" in data
    assert data["export_info"]["app"] == "OddsEngine"


@pytest.mark.anyio
async def test_export_has_match_details(client: AsyncClient):
    create_resp = await client.post("/api/combinations")
    comb_id = create_resp.json()["combination"]["id"]
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_001"})
    await client.post(f"/api/combinations/{comb_id}/matches", json={"match_id": "match_002"})

    response = await client.get(f"/api/combinations/{comb_id}/export")
    data = response.json()
    assert len(data["matches"]) == 2
    for m in data["matches"]:
        assert "match_id" in m
        assert "players" in m
        assert "probability" in m
        assert "favorite" in m

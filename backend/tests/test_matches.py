"""
Pruebas para la consulta de partidos de tenis (HU-01).
Los fixtures (client, clean_storage) están en conftest.py.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.anyio
async def test_list_matches_returns_200(client: AsyncClient):
    response = await client.get("/api/matches")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.anyio
async def test_match_has_required_fields(client: AsyncClient):
    response = await client.get("/api/matches")
    data = response.json()
    match = data[0]
    assert "id" in match
    assert "player_home" in match
    assert "player_away" in match
    assert "tournament" in match
    assert "date" in match
    assert "status" in match
    player = match["player_home"]
    assert "id" in player
    assert "name" in player
    assert "country" in player
    tournament = match["tournament"]
    assert "id" in tournament
    assert "name" in tournament
    assert "surface" in tournament
    assert "category" in tournament


@pytest.mark.anyio
async def test_filter_by_status_upcoming(client: AsyncClient):
    response = await client.get("/api/matches", params={"status": "upcoming"})
    assert response.status_code == 200
    data = response.json()
    for match in data:
        assert match["status"] == "upcoming"


@pytest.mark.anyio
async def test_filter_by_status_finished(client: AsyncClient):
    response = await client.get("/api/matches", params={"status": "finished"})
    assert response.status_code == 200
    data = response.json()
    for match in data:
        assert match["status"] == "finished"


@pytest.mark.anyio
async def test_filter_by_tournament(client: AsyncClient):
    response = await client.get("/api/matches", params={"tournament": "Roland Garros"})
    assert response.status_code == 200
    data = response.json()
    for match in data:
        assert "roland garros" in match["tournament"]["name"].lower()


@pytest.mark.anyio
async def test_get_match_by_id(client: AsyncClient):
    response = await client.get("/api/matches/match_001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "match_001"


@pytest.mark.anyio
async def test_get_match_not_found(client: AsyncClient):
    response = await client.get("/api/matches/nonexistent")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_matches_sorted_by_date(client: AsyncClient):
    response = await client.get("/api/matches")
    data = response.json()
    dates = [m["date"] for m in data]
    assert dates == sorted(dates)


@pytest.mark.anyio
async def test_finished_match_has_score(client: AsyncClient):
    response = await client.get("/api/matches", params={"status": "finished"})
    data = response.json()
    for match in data:
        assert match["score"] is not None

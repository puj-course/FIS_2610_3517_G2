"""
Pruebas para el servicio y endpoint de estadísticas (Semana 4).
Los fixtures (client, clean_storage) están en conftest.py.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_stats_returns_200(client: AsyncClient):
    """Stats de un partido válido retorna 200."""
    response = await client.get("/api/matches/match_001/stats")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_stats_has_both_players(client: AsyncClient):
    """Las stats incluyen datos de ambos jugadores."""
    response = await client.get("/api/matches/match_001/stats")
    data = response.json()
    assert "player_home_stats" in data
    assert "player_away_stats" in data
    assert data["player_home_stats"]["player_name"] is not None
    assert data["player_away_stats"]["player_name"] is not None


@pytest.mark.anyio
async def test_stats_has_head_to_head(client: AsyncClient):
    """Las stats incluyen Head-to-Head cuando existe."""
    response = await client.get("/api/matches/match_001/stats")
    data = response.json()
    # H2H puede ser null si no hay historial
    if data["head_to_head"] is not None:
        assert "player1_wins" in data["head_to_head"]
        assert "player2_wins" in data["head_to_head"]


@pytest.mark.anyio
async def test_stats_win_rates_in_range(client: AsyncClient):
    """Los win rates están entre 0 y 100."""
    response = await client.get("/api/matches/match_001/stats")
    data = response.json()
    home = data["player_home_stats"]
    away = data["player_away_stats"]
    assert 0 <= home["overall_win_rate"] <= 100
    assert 0 <= away["overall_win_rate"] <= 100
    assert 0 <= home["surface_win_rate"] <= 100
    assert 0 <= away["surface_win_rate"] <= 100


@pytest.mark.anyio
async def test_stats_has_recent_form(client: AsyncClient):
    """Las stats incluyen forma reciente."""
    response = await client.get("/api/matches/match_001/stats")
    data = response.json()
    home = data["player_home_stats"]
    assert len(home["recent_form"]) > 0
    assert all(r in ["W", "L"] for r in home["recent_form"])


@pytest.mark.anyio
async def test_stats_has_surface(client: AsyncClient):
    """Las stats incluyen la superficie del torneo."""
    response = await client.get("/api/matches/match_001/stats")
    data = response.json()
    assert "surface" in data
    assert data["surface"] in ["hard", "clay", "grass", "carpet"]


@pytest.mark.anyio
async def test_stats_match_not_found(client: AsyncClient):
    """Stats de partido inexistente retorna 404."""
    response = await client.get("/api/matches/fake_match/stats")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_stats_required_fields(client: AsyncClient):
    """Todos los campos requeridos están presentes."""
    response = await client.get("/api/matches/match_001/stats")
    data = response.json()
    assert "match_id" in data
    assert "player_home_stats" in data
    assert "player_away_stats" in data
    assert "surface" in data
    home = data["player_home_stats"]
    for field in ["player_id", "player_name", "overall_win_rate", "surface_win_rate", "recent_form", "total_matches"]:
        assert field in home, f"Campo faltante: {field}"

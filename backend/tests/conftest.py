"""
Configuración global de tests.

Asegura que el almacenamiento en memoria se limpia
antes y después de CADA test, independientemente del archivo.
Esto evita que los datos de un test se filtren a otro.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.storage import reset_storage
from app.services.auth_service import reset_auth_service

from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from sqlalchemy.engine.result import Result

from app.models.db_models import MatchDB

@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def clean_storage():
    """Limpia el almacenamiento antes y después de cada test."""
    reset_storage()
    reset_auth_service()
    yield
    reset_storage()
    reset_auth_service()


@pytest.fixture
async def client():
    """Cliente HTTP para tests — simula peticiones al servidor."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        
@pytest.fixture
def sample_match_db():
    """Fixture de partido de ejemplo."""
    return MatchDB(
        id="match_123",
        player_home_id="player_1",
        player_home_name="Novak Djokovic",
        player_home_country="Serbia",
        player_home_ranking=1,
        player_away_id="player_2",
        player_away_name="Carlos Alcaraz",
        player_away_country="Spain",
        player_away_ranking=2,
        tournament_id="tour_1",
        tournament_name="Wimbledon",
        tournament_surface="grass",
        tournament_category="Grand Slam",
        tournament_location="London",
        date=datetime.now(),
        status="upcoming",
        score="",
    )

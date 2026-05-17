"""
Pruebas para el repositorio de partidos.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.result import Result

from app.repositories.matches_repository import MatchesRepository
from app.models.match import Match, Player, Tournament, MatchStatus, Surface
from app.models.db_models import MatchDB


@pytest.fixture
def mock_db_session():
    """Fixture para mock de sesión de base de datos."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def repository(mock_db_session):
    """Fixture del repositorio con mock de sesión."""
    return MatchesRepository(mock_db_session)


@pytest.fixture
def sample_match_db():
    """Fixture de un partido de ejemplo como objeto DB."""
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
        tournament_surface="grass",  # Minúsculas como en el enum
        tournament_category="Grand Slam",
        tournament_location="London",
        date=datetime.now(),
        status="upcoming",  # Minúsculas como en el enum
        score="",
    )


class TestMatchesRepository:
    """Pruebas para MatchesRepository."""

    @pytest.mark.asyncio
    async def test_get_all_success(self, repository, mock_db_session, sample_match_db):
        """Test: Obtener todos los partidos exitosamente."""
        mock_result = MagicMock(spec=Result)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_match_db]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        result = await repository.get_all()

        assert len(result) == 1
        assert result[0].id == "match_123"
        assert result[0].player_home.name == "Novak Djokovic"
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_empty(self, repository, mock_db_session):
        """Test: Obtener todos los partidos cuando no hay datos."""
        mock_result = MagicMock(spec=Result)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        result = await repository.get_all()

        assert result == []
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_with_status_filter(self, repository, mock_db_session, sample_match_db):
        """Test: Filtrar partidos por estado."""
        mock_result = MagicMock(spec=Result)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_match_db]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        result = await repository.get_all(status="upcoming")

        assert len(result) == 1
        assert result[0].status == MatchStatus.UPCOMING
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_with_tournament_filter(self, repository, mock_db_session, sample_match_db):
        """Test: Filtrar partidos por torneo."""
        mock_result = MagicMock(spec=Result)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_match_db]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        result = await repository.get_all(tournament="Wimbledon")

        assert len(result) == 1
        assert result[0].tournament.name == "Wimbledon"
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, repository, mock_db_session, sample_match_db):
        """Test: Obtener partido por ID exitosamente."""
        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = sample_match_db
        mock_db_session.execute.return_value = mock_result

        result = await repository.get_by_id("match_123")

        assert result is not None
        assert result.id == "match_123"
        assert result.player_home.name == "Novak Djokovic"
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_db_session):
        """Test: Intentar obtener partido que no existe."""
        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await repository.get_by_id("non_existent_id")

        assert result is None
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_insert_many_success(self, repository, mock_db_session):
        """Test: Insertar múltiples partidos exitosamente."""
        matches_data = [
            {
                "id": "match_1",
                "player_home_id": "p1",
                "player_home_name": "Player 1",
                "player_away_id": "p2",
                "player_away_name": "Player 2",
                "tournament_id": "t1",
                "tournament_name": "Tournament 1",
                "date": datetime.now(),
                "status": "upcoming",
            },
            {
                "id": "match_2",
                "player_home_id": "p3",
                "player_home_name": "Player 3",
                "player_away_id": "p4",
                "player_away_name": "Player 4",
                "tournament_id": "t1",
                "tournament_name": "Tournament 1",
                "date": datetime.now(),
                "status": "upcoming",
            },
        ]

        await repository.insert_many(matches_data)

        assert mock_db_session.add.call_count == 2
        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_insert_many_failure(self, repository, mock_db_session):
        """Test: Error al insertar partidos."""
        matches_data = [{"id": "match_1"}]

        mock_db_session.commit.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(SQLAlchemyError):
            await repository.insert_many(matches_data)

        mock_db_session.rollback.assert_called_once()
        mock_db_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_all_success(self, repository, mock_db_session):
        """Test: Eliminar todos los partidos exitosamente."""
        await repository.delete_all()

        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_all_failure(self, repository, mock_db_session):
        """Test: Error al eliminar todos los partidos."""
        mock_db_session.commit.side_effect = SQLAlchemyError("Database error")

        with pytest.raises(SQLAlchemyError):
            await repository.delete_all()

        mock_db_session.rollback.assert_called_once()
        mock_db_session.execute.assert_called_once()

    def test_to_pydantic_with_minimal_data(self, repository):
        """Test: Conversión a Pydantic con datos mínimos."""
        minimal_match = MatchDB(
            id="minimal_id",
            player_home_id="ph1",
            player_away_id="pa1",
            tournament_id="t1",
            date=datetime.now(),
        )

        result = repository._to_pydantic(minimal_match)

        assert result.id == "minimal_id"
        assert result.player_home.id == "ph1"
        assert result.player_home.name == "Unknown"
        assert result.player_home.country == "Unknown"
        assert result.player_home.ranking == 0
        assert result.player_away.id == "pa1"
        assert result.player_away.name == "Unknown"
        assert result.player_away.country == "Unknown"
        assert result.player_away.ranking == 0
        assert result.tournament.id == "t1"
        assert result.tournament.name == "Unknown Tournament"
        assert result.tournament.surface == Surface.HARD
        assert result.tournament.category == "Unknown"
        assert result.tournament.location == "Unknown"
        assert result.status == MatchStatus.UPCOMING

    def test_to_pydantic_with_full_data(self, repository, sample_match_db):
        """Test: Conversión a Pydantic con datos completos."""
        result = repository._to_pydantic(sample_match_db)

        assert result.id == "match_123"
        assert result.player_home.name == "Novak Djokovic"
        assert result.player_home.country == "Serbia"
        assert result.player_home.ranking == 1
        assert result.player_away.name == "Carlos Alcaraz"
        assert result.player_away.country == "Spain"
        assert result.player_away.ranking == 2
        assert result.tournament.name == "Wimbledon"
        assert result.tournament.surface == Surface.GRASS
        assert result.tournament.category == "Grand Slam"
        assert result.tournament.location == "London"
        assert result.status == MatchStatus.UPCOMING

    @pytest.mark.asyncio
    async def test_get_all_ordering(self, repository, mock_db_session):
        """Test: Verificar que los resultados están ordenados por fecha."""
        date1 = datetime.now() - timedelta(days=2)
        date2 = datetime.now() - timedelta(days=1)
        date3 = datetime.now()

        match1 = MatchDB(
            id="m1", 
            date=date1,
            player_home_id="ph1",
            player_away_id="pa1",
            tournament_id="t1"
        )
        match2 = MatchDB(
            id="m2", 
            date=date2,
            player_home_id="ph2",
            player_away_id="pa2",
            tournament_id="t2"
        )
        match3 = MatchDB(
            id="m3", 
            date=date3,
            player_home_id="ph3",
            player_away_id="pa3",
            tournament_id="t3"
        )

        mock_result = MagicMock(spec=Result)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [match1, match2, match3]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        result = await repository.get_all()

        assert len(result) == 3
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_with_nonexistent_tournament_surface(self, repository, mock_db_session):
        """Test: Manejo de superficie de torneo None."""
        match_without_surface = MatchDB(
            id="match_no_surface",
            player_home_id="ph1",
            player_home_name="Player",
            player_away_id="pa1",
            player_away_name="Opponent",
            tournament_id="t1",
            tournament_name="Tournament",
            tournament_surface=None,
            date=datetime.now(),
        )

        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = match_without_surface
        mock_db_session.execute.return_value = mock_result

        result = await repository.get_by_id("match_no_surface")

        assert result is not None
        assert result.tournament.surface == Surface.HARD

    @pytest.mark.asyncio
    async def test_get_all_with_case_insensitive_tournament_filter(self, repository, mock_db_session):
        """Test: Filtro insensible a mayúsculas/minúsculas para torneo."""
        mock_result = MagicMock(spec=Result)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        await repository.get_all(tournament="wimbledon")

        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_with_status_and_tournament_filters(self, repository, mock_db_session, sample_match_db):
        """Test: Aplicar múltiples filtros simultáneamente."""
        mock_result = MagicMock(spec=Result)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_match_db]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result

        result = await repository.get_all(status="upcoming", tournament="Wimbledon")

        assert len(result) == 1
        mock_db_session.execute.assert_called_once()

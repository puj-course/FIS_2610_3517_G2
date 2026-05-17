"""
Pruebas para el repositorio de partidos usando Factory pattern.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError

from app.models.match import MatchStatus, Surface
from app.models.db_models import MatchDB


class TestMatchesRepository:
    """Pruebas para MatchesRepository usando Factory."""
    
    @pytest.mark.asyncio
    async def test_get_all_success(self, repository, db_session, match_factory):
        """Test: Obtener todos los partidos exitosamente."""
        # Crear 2 matches usando factory
        matches = match_factory.create_batch(2)
        for match in matches:
            db_session.add(match)
        await db_session.commit()
        
        result = await repository.get_all()
        
        # Verificar que se retornan los 2 matches insertados
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_all_empty(self, repository):
        """Test: Obtener todos los partidos cuando no hay datos."""
        result = await repository.get_all()
        
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_with_status_filter(self, repository, db_session, match_factory):
        """Test: Filtrar partidos por estado."""
        # Crear matches con diferentes estados
        upcoming_match = match_factory.create(status="upcoming")
        finished_match = match_factory.create(status="finished")
        
        db_session.add_all([upcoming_match, finished_match])
        await db_session.commit()
        
        result = await repository.get_all(status="upcoming")
        
        assert len(result) == 1
        assert result[0].status == MatchStatus.UPCOMING

    @pytest.mark.asyncio
    async def test_get_all_with_tournament_filter(self, repository, db_session, match_factory):
        """Test: Filtrar partidos por torneo."""
        wimbledon_match = match_factory.create(tournament_name="Wimbledon")
        roland_match = match_factory.create(tournament_name="Roland Garros")
        
        db_session.add_all([wimbledon_match, roland_match])
        await db_session.commit()
        
        result = await repository.get_all(tournament="Wimbledon")
        
        assert len(result) == 1
        assert result[0].tournament.name == "Wimbledon"

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, repository, db_session, match_factory):
        """Test: Obtener partido por ID exitosamente."""
        match = match_factory.create(id="test_match_123")
        db_session.add(match)
        await db_session.commit()
        
        result = await repository.get_by_id("test_match_123")
        
        assert result is not None
        assert result.id == "test_match_123"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test: Intentar obtener partido que no existe."""
        result = await repository.get_by_id("non_existent_id")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_insert_many_success(self, repository, match_factory):
        """Test: Insertar múltiples partidos exitosamente."""
        # Usar factory para crear los datos
        match1 = match_factory.create(id="new1")
        match2 = match_factory.create(id="new2")
        
        matches_data = [
            {
                "id": match1.id,
                "player_home_id": match1.player_home_id,
                "player_home_name": match1.player_home_name,
                "player_home_country": match1.player_home_country,
                "player_home_ranking": match1.player_home_ranking,
                "player_away_id": match1.player_away_id,
                "player_away_name": match1.player_away_name,
                "player_away_country": match1.player_away_country,
                "player_away_ranking": match1.player_away_ranking,
                "tournament_id": match1.tournament_id,
                "tournament_name": match1.tournament_name,
                "tournament_surface": match1.tournament_surface,
                "tournament_category": match1.tournament_category,
                "tournament_location": match1.tournament_location,
                "date": match1.date,
                "status": match1.status,
                "score": match1.score,
            },
            {
                "id": match2.id,
                "player_home_id": match2.player_home_id,
                "player_home_name": match2.player_home_name,
                "player_home_country": match2.player_home_country,
                "player_home_ranking": match2.player_home_ranking,
                "player_away_id": match2.player_away_id,
                "player_away_name": match2.player_away_name,
                "player_away_country": match2.player_away_country,
                "player_away_ranking": match2.player_away_ranking,
                "tournament_id": match2.tournament_id,
                "tournament_name": match2.tournament_name,
                "tournament_surface": match2.tournament_surface,
                "tournament_category": match2.tournament_category,
                "tournament_location": match2.tournament_location,
                "date": match2.date,
                "status": match2.status,
                "score": match2.score,
            }
        ]
        
        await repository.insert_many(matches_data)
        
        # Verificar que se insertaron
        result = await repository.get_all()
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_insert_many_failure(self, repository, match_factory):
        """Test: Error al insertar partidos con datos inválidos."""
        # Crear datos que causarán error (por ejemplo, sin ID)
        invalid_data = [{"id": None}]  # Esto debería fallar
        
        with pytest.raises(SQLAlchemyError):
            await repository.insert_many(invalid_data)

    @pytest.mark.asyncio
    async def test_delete_all_success(self, repository, db_session, match_factory):
        """Test: Eliminar todos los partidos exitosamente."""
        # Insertar algunos matches
        matches = match_factory.create_batch(3)
        for match in matches:
            db_session.add(match)
        await db_session.commit()
        
        # Verificar que hay matches
        result_before = await repository.get_all()
        assert len(result_before) == 3
        
        # Eliminar todos
        await repository.delete_all()
        
        # Verificar que no hay matches
        result_after = await repository.get_all()
        assert len(result_after) == 0

    @pytest.mark.asyncio
    async def test_delete_all_failure(self, repository, db_session, monkeypatch):
        """Test: Error al eliminar todos los partidos."""
        # Simular error en commit
        async def mock_commit():
            raise SQLAlchemyError("Database error")
        
        monkeypatch.setattr(db_session, "commit", mock_commit)
        
        with pytest.raises(SQLAlchemyError):
            await repository.delete_all()

    def test_to_pydantic_with_minimal_data(self, repository, match_factory):
        """Test: Conversión a Pydantic con datos mínimos."""
        # Usar factory para crear match con datos mínimos; forzamos status para el assert
        minimal_match = match_factory.create_minimal_match(id="minimal_id", status="upcoming")
        
        result = repository._to_pydantic(minimal_match)
        
        assert result.id == "minimal_id"
        assert result.player_home.name == "Unknown"
        assert result.player_home.country == "Unknown"
        assert result.player_home.ranking == 0
        assert result.player_away.name == "Unknown"
        assert result.player_away.country == "Unknown"
        assert result.player_away.ranking == 0
        assert result.tournament.name == "Unknown Tournament"
        assert result.tournament.surface == Surface.HARD
        assert result.status == MatchStatus.UPCOMING

    def test_to_pydantic_with_full_data(self, repository, match_factory):
        """Test: Conversión a Pydantic con datos completos."""
        full_match = match_factory.create(
            id="full_match",
            player_home_name="Novak Djokovic",
            player_home_country="Serbia",
            player_home_ranking=1,
            player_away_name="Carlos Alcaraz",
            player_away_country="Spain",
            player_away_ranking=2,
            tournament_name="Wimbledon",
            tournament_surface="grass",
            tournament_category="Grand Slam",
            status="finished",
        )
        
        result = repository._to_pydantic(full_match)
        
        assert result.player_home.name == "Novak Djokovic"
        assert result.tournament.surface == Surface.GRASS
        assert result.status == MatchStatus.FINISHED

    def test_to_pydantic_with_uppercase_values(self, repository, match_factory):
        """Test: Conversión con valores en mayúsculas."""
        uppercase_match = match_factory.create(
            tournament_surface="GRASS",
            status="FINISHED"
        )
        
        result = repository._to_pydantic(uppercase_match)
        
        assert result.tournament.surface == Surface.GRASS
        assert result.status == MatchStatus.FINISHED

    @pytest.mark.asyncio
    async def test_get_all_ordering(self, repository, db_session, match_factory):
        """Test: Verificar ordenamiento por fecha."""
        # Crear matches con diferentes fechas
        date1 = datetime.now() - timedelta(days=2)
        date2 = datetime.now() - timedelta(days=1)
        date3 = datetime.now()
        
        match1 = match_factory.create_with_fixed_date(date1, id="match_early")
        match2 = match_factory.create_with_fixed_date(date2, id="match_mid")
        match3 = match_factory.create_with_fixed_date(date3, id="match_late")
        
        db_session.add_all([match1, match2, match3])
        await db_session.commit()
        
        result = await repository.get_all()
        
        # Verificar que están ordenados (el más antiguo primero según order_by)
        # Nota: Tu repositorio usa order_by(MatchDB.date)
        dates = [m.date for m in result]
        assert dates == sorted(dates)

    @pytest.mark.asyncio
    async def test_get_by_id_with_nonexistent_tournament_surface(self, repository, db_session, match_factory):
        """Test: La superficie 'carpet' se convierte correctamente al enum Surface."""
        match = match_factory.create(
            id="unknown_surface_match",
            tournament_surface="carpet",
        )
        db_session.add(match)
        await db_session.commit()

        result = await repository.get_by_id("unknown_surface_match")

        assert result is not None
        # "carpet" es un valor válido del enum Surface
        assert result.tournament.surface == Surface.CARPET

    @pytest.mark.asyncio
    async def test_get_all_with_case_insensitive_tournament_filter(self, repository, db_session, match_factory):
        """Test: Filtro insensible a mayúsculas/minúsculas."""
        match = match_factory.create(tournament_name="Wimbledon Championship")
        db_session.add(match)
        await db_session.commit()
        
        # Buscar con minúsculas
        result = await repository.get_all(tournament="wimbledon")
        
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_all_with_status_and_tournament_filters(self, repository, db_session, match_factory):
        """Test: Aplicar múltiples filtros simultáneamente."""
        match = match_factory.create(
            tournament_name="Wimbledon",
            status="upcoming"
        )
        db_session.add(match)
        await db_session.commit()
        
        result = await repository.get_all(status="upcoming", tournament="Wimbledon")
        
        assert len(result) == 1

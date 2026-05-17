"""
Repositorio de partidos — capa de acceso a datos PostgreSQL.

Maneja todas las operaciones CRUD de la tabla matches.
"""

import logging
from typing import Optional, List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.models.db_models import MatchDB
from app.models.match import Match, Player, Tournament, MatchStatus, Surface

logger = logging.getLogger("oddsengine")


class MatchesRepository:
    """Repositorio para operaciones CRUD de partidos en PostgreSQL."""

    def __init__(self, db: AsyncSession):
        """
        Inicializa el repositorio con la sesión de base de datos.

        Args:
            db (AsyncSession): Sesión asíncrona de SQLAlchemy.
        """
        self.db = db

    async def get_all(
        self, status: Optional[str] = None, tournament: Optional[str] = None
    ) -> List[Match]:
        """
        Obtener todos los partidos, con filtros opcionales.

        Args:
            status (Optional[str]): Filtrar por estado del partido.
            tournament (Optional[str]): Filtrar por nombre de torneo.

        Returns:
            List[Match]: Lista de partidos como modelos Pydantic.
        """
        query = select(MatchDB)
        if status:
            query = query.where(MatchDB.status == status)
        if tournament:
            query = query.where(MatchDB.tournament_name.ilike(f"%{tournament}%"))
        query = query.order_by(MatchDB.date)

        result = await self.db.execute(query)
        rows = result.scalars().all()
        return [self._to_pydantic(row) for row in rows]

    async def get_by_id(self, match_id: str) -> Optional[Match]:
        """
        Obtener un partido por ID.

        Args:
            match_id (str): ID del partido.

        Returns:
            Optional[Match]: Modelo Pydantic del partido, o None si no existe.
        """
        query = select(MatchDB).where(MatchDB.id == match_id)
        result = await self.db.execute(query)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_pydantic(row)

    async def insert_many(self, matches: List[dict]):
        """
        Insertar múltiples partidos (para seed).

        Args:
            matches (List[dict]): Lista de diccionarios con datos de partidos.

        Raises:
            SQLAlchemyError: Si ocurre un error al insertar los registros.
        """
        try:
            for match_data in matches:
                db_match = MatchDB(**match_data)
                self.db.add(db_match)
            await self.db.commit()
            logger.info(f"Insertados {len(matches)} partidos en PostgreSQL")
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error al insertar partidos: {e}")
            raise

    async def delete_all(self):
        """
        Eliminar todos los partidos (para seed con --clean).

        Raises:
            SQLAlchemyError: Si ocurre un error al eliminar los registros.
        """
        try:
            await self.db.execute(delete(MatchDB))
            await self.db.commit()
            logger.info("Todos los partidos eliminados de PostgreSQL")
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error al eliminar partidos: {e}")
            raise

    def _to_pydantic(self, row: MatchDB) -> Match:
        """
        Convertir un registro de BD a modelo Pydantic.

        Args:
            row (MatchDB): Registro de SQLAlchemy.

        Returns:
            Match: Modelo Pydantic correspondiente.
        """
        # Manejo seguro de datos faltantes
        return Match(
            id=row.id,
            player_home=Player(
                id=row.player_home_id or "",
                name=row.player_home_name or "Unknown",
                country=row.player_home_country or "Unknown",
                ranking=row.player_home_ranking or 0,
            ),
            player_away=Player(
                id=row.player_away_id or "",
                name=row.player_away_name or "Unknown",
                country=row.player_away_country or "Unknown",
                ranking=row.player_away_ranking or 0,
            ),
            tournament=Tournament(
                id=row.tournament_id or "",
                name=row.tournament_name or "Unknown Tournament",
                surface=Surface(row.tournament_surface.lower()) if row.tournament_surface else Surface.HARD,
                category=row.tournament_category or "Unknown",
                location=row.tournament_location or "Unknown",
            ),
            date=row.date,
            status=MatchStatus(row.status.lower()) if row.status else MatchStatus.UPCOMING,
            score=row.score,
        )
        
"""
Pruebas específicas para cubrir líneas del repositorio.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.engine.result import Result

from app.repositories.matches_repository import MatchesRepository
from app.models.match import MatchStatus, Surface
from app.models.db_models import MatchDB


class TestMatchesRepositoryFullCoverage:
    """Pruebas para cubrir todas las líneas del repositorio."""

    @pytest.mark.asyncio
    async def test_insert_many_success_with_logging(self, repository, mock_db_session):
        """Cubrir líneas 73-81: insert_many exitoso con logging."""
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
            }
        ]

        # Mock del logger
        with patch('app.repositories.matches_repository.logger') as mock_logger:
            await repository.insert_many(matches_data)
            
            # Verificar que se llamó al logger.info (línea 79)
            mock_logger.info.assert_called_once_with(
                f"Insertados {len(matches_data)} partidos en PostgreSQL"
            )
        
        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_insert_many_failure_with_logging(self, repository, mock_db_session):
        """Cubrir líneas 80-84: insert_many con error y logging."""
        matches_data = [{"id": "match_1"}]
        
        # Simular error en commit
        mock_db_session.commit.side_effect = SQLAlchemyError("Database error")

        with patch('app.repositories.matches_repository.logger') as mock_logger:
            with pytest.raises(SQLAlchemyError):
                await repository.insert_many(matches_data)
            
            # Verificar que se llamó al logger.error (línea 82)
            mock_logger.error.assert_called_once_with(
                "Error al insertar partidos: Database error"
            )
        
        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_all_success_with_logging(self, repository, mock_db_session):
        """Cubrir líneas 95-99: delete_all exitoso con logging."""
        mock_result = MagicMock(spec=Result)
        mock_db_session.execute.return_value = mock_result

        with patch('app.repositories.matches_repository.logger') as mock_logger:
            await repository.delete_all()
            
            # Verificar logger.info (línea 98)
            mock_logger.info.assert_called_once_with(
                "Todos los partidos eliminados de PostgreSQL"
            )
        
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_all_failure_with_logging(self, repository, mock_db_session):
        """Cubrir líneas 99-103: delete_all con error y logging."""
        mock_db_session.commit.side_effect = SQLAlchemyError("Database error")

        with patch('app.repositories.matches_repository.logger') as mock_logger:
            with pytest.raises(SQLAlchemyError):
                await repository.delete_all()
            
            # Verificar logger.error (línea 101)
            mock_logger.error.assert_called_once_with(
                "Error al eliminar partidos: Database error"
            )
        
        mock_db_session.rollback.assert_called_once()

    def test_to_pydantic_all_fields_none(self, repository):
        """Cubrir líneas 123-144: to_pydantic con todos los campos None."""
        minimal_match = MatchDB(
            id="test_id",
            player_home_id=None,
            player_home_name=None,
            player_home_country=None,
            player_home_ranking=None,
            player_away_id=None,
            player_away_name=None,
            player_away_country=None,
            player_away_ranking=None,
            tournament_id=None,
            tournament_name=None,
            tournament_surface=None,
            tournament_category=None,
            tournament_location=None,
            date=datetime.now(),
            status=None,
            score=None,
        )
        
        result = repository._to_pydantic(minimal_match)
        
        # Verificar valores por defecto (líneas 124-127, 130-133, 136-140)
        assert result.player_home.id == ""
        assert result.player_home.name == "Unknown"
        assert result.player_home.country == "Unknown"
        assert result.player_home.ranking == 0
        assert result.player_away.id == ""
        assert result.player_away.name == "Unknown"
        assert result.player_away.country == "Unknown"
        assert result.player_away.ranking == 0
        assert result.tournament.id == ""
        assert result.tournament.name == "Unknown Tournament"
        assert result.tournament.surface == Surface.HARD
        assert result.tournament.category == "Unknown"
        assert result.tournament.location == "Unknown"
        assert result.status == MatchStatus.UPCOMING

    def test_to_pydantic_with_all_valid_data(self, repository):
        """Cubrir líneas 123-144 con datos válidos."""
        valid_match = MatchDB(
            id="valid_id",
            player_home_id="ph1",
            player_home_name="Roger Federer",
            player_home_country="Switzerland",
            player_home_ranking=1,
            player_away_id="pa1",
            player_away_name="Rafael Nadal",
            player_away_country="Spain",
            player_away_ranking=2,
            tournament_id="t1",
            tournament_name="Wimbledon",
            tournament_surface="grass",
            tournament_category="Grand Slam",
            tournament_location="London",
            date=datetime.now(),
            status="finished",
            score="6-3, 6-4",
        )
        
        result = repository._to_pydantic(valid_match)
        
        # Verificar todos los valores (líneas 124-144)
        assert result.id == "valid_id"
        assert result.player_home.id == "ph1"
        assert result.player_home.name == "Roger Federer"
        assert result.player_home.country == "Switzerland"
        assert result.player_home.ranking == 1
        assert result.player_away.id == "pa1"
        assert result.player_away.name == "Rafael Nadal"
        assert result.player_away.country == "Spain"
        assert result.player_away.ranking == 2
        assert result.tournament.id == "t1"
        assert result.tournament.name == "Wimbledon"
        assert result.tournament.surface == Surface.GRASS
        assert result.tournament.category == "Grand Slam"
        assert result.tournament.location == "London"
        assert result.status == MatchStatus.FINISHED
        assert result.score == "6-3, 6-4"

    def test_to_pydantic_with_uppercase_status_and_surface(self, repository):
        """Cubrir líneas 138 y 143: conversión de mayúsculas a minúsculas."""
        uppercase_match = MatchDB(
            id="uppercase",
            player_home_id="ph1",
            player_home_name="Player",
            player_away_id="pa1",
            player_away_name="Opponent",
            tournament_id="t1",
            tournament_name="Tournament",
            tournament_surface="GRASS",  # Mayúsculas
            date=datetime.now(),
            status="FINISHED",  # Mayúsculas
        )
        
        result = repository._to_pydantic(uppercase_match)
        
        # Verificar que .lower() funcionó (líneas 138, 143)
        assert result.tournament.surface == Surface.GRASS
        assert result.status == MatchStatus.FINISHED

    @pytest.mark.asyncio
    async def test_get_all_with_filters_combined(self, repository, mock_db_session, sample_match_db):
        """Cubrir líneas 45-54 con ambos filtros activos."""
        mock_result = MagicMock(spec=Result)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_match_db]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        # Activar ambos filtros (líneas 46-50)
        result = await repository.get_all(status="upcoming", tournament="Wimbledon")
        
        assert len(result) == 1
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_none_row(self, repository, mock_db_session):
        """Cubrir líneas 69-70: row is None."""
        mock_result = MagicMock(spec=Result)
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await repository.get_by_id("nonexistent")
        
        assert result is None  # línea 70

    @pytest.mark.asyncio
    async def test_insert_many_empty_list(self, repository, mock_db_session):
        """Cubrir el bucle for con lista vacía."""
        await repository.insert_many([])
        
        # No debería llamar a add
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_no_filters(self, repository, mock_db_session, sample_match_db):
        """Cubrir líneas 45-54 sin filtros."""
        mock_result = MagicMock(spec=Result)
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_match_db]
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        # Sin filtros (líneas 46 y 48 no entran)
        result = await repository.get_all()
        
        assert len(result) == 1
        mock_db_session.execute.assert_called_once()


# Prueba de integración para imports (opcional)
def test_imports_are_accessible():
    """Verificar que los imports funcionan (cubre líneas 10-15)."""
    from sqlalchemy import select, delete
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.exc import SQLAlchemyError
    from app.models.db_models import MatchDB
    from app.models.match import Match, Player, Tournament, MatchStatus, Surface
    
    assert select is not None
    assert delete is not None
    assert AsyncSession is not None
    assert SQLAlchemyError is not None
    assert MatchDB is not None
    assert Match is not None
    assert Player is not None
    assert Tournament is not None
    assert MatchStatus is not None
    assert Surface is not None

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
            logger.info("Insertados %s partidos en PostgreSQL", len(matches))
        except SQLAlchemyError:
            await self.db.rollback()
            logger.exception("Error al insertar partidos")
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
        except SQLAlchemyError:
            await self.db.rollback()
            logger.exception("Error al eliminar partidos")
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

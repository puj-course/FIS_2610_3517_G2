"""
Repositorio de partidos — capa de acceso a datos PostgreSQL.

Maneja todas las operaciones CRUD de la tabla matches.
"""

import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import MatchDB
from app.models.match import Match, Player, Tournament, MatchStatus, Surface

logger = logging.getLogger("oddsengine")


class MatchesRepository:
    """Repositorio para operaciones CRUD de partidos en PostgreSQL."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self, status: Optional[str] = None, tournament: Optional[str] = None
    ) -> list[Match]:
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
        query = select(MatchDB).where(MatchDB.id == match_id)
        result = await self.db.execute(query)
        row = result.scalar_one_or_none()

        if row is None:
            return None
        return self._to_pydantic(row)

    async def insert_many(self, matches: list[dict]):
        for match_data in matches:
            db_match = MatchDB(**match_data)
            self.db.add(db_match)
        await self.db.commit()
        logger.info(f"Insertados {len(matches)} partidos en PostgreSQL")

    async def delete_all(self):
        from sqlalchemy import delete
        await self.db.execute(delete(MatchDB))
        await self.db.commit()
        logger.info("Todos los partidos eliminados de PostgreSQL")

    def _to_pydantic(self, row: MatchDB) -> Match:
        return Match(
            id=row.id,
            player_home=Player(
                id=row.player_home_id,
                name=row.player_home_name,
                country=row.player_home_country,
                ranking=row.player_home_ranking,
            ),
            player_away=Player(
                id=row.player_away_id,
                name=row.player_away_name,
                country=row.player_away_country,
                ranking=row.player_away_ranking,
            ),
            tournament=Tournament(
                id=row.tournament_id,
                name=row.tournament_name,
                surface=Surface(row.tournament_surface),
                category=row.tournament_category,
                location=row.tournament_location,
            ),
            date=row.date,
            status=MatchStatus(row.status),
            score=row.score,
        )

"""
Script de seed: inserta datos iniciales en PostgreSQL.

Uso:
    python scripts/seed_database.py          # Insertar datos
    python scripts/seed_database.py --clean  # Limpiar e insertar

Requiere: PostgreSQL corriendo y DATABASE_URL configurado en .env
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import engine, AsyncSessionLocal, create_tables
from app.models.db_models import MatchDB, PlayerStatsDB, HeadToHeadDB
from app.providers.mock_provider import MockMatchProvider
from app.providers.mock_stats_provider import PLAYER_STATS, SURFACE_WIN_RATES, H2H_DATA
from sqlalchemy import delete
import json


async def seed_matches(session, clean=False):
    if clean:
        await session.execute(delete(MatchDB))
        print("🗑️  Partidos eliminados")

    provider = MockMatchProvider()
    matches = await provider.get_matches()

    for m in matches:
        db_match = MatchDB(
            id=m.id,
            player_home_id=m.player_home.id,
            player_home_name=m.player_home.name,
            player_home_country=m.player_home.country,
            player_home_ranking=m.player_home.ranking,
            player_away_id=m.player_away.id,
            player_away_name=m.player_away.name,
            player_away_country=m.player_away.country,
            player_away_ranking=m.player_away.ranking,
            tournament_id=m.tournament.id,
            tournament_name=m.tournament.name,
            tournament_surface=m.tournament.surface.value,
            tournament_category=m.tournament.category,
            tournament_location=m.tournament.location,
            date=m.date,
            status=m.status.value,
            score=m.score,
        )
        session.add(db_match)

    await session.commit()
    print(f"✅ {len(matches)} partidos insertados")


async def seed_player_stats(session, clean=False):
    if clean:
        await session.execute(delete(PlayerStatsDB))
        print("🗑️  Estadísticas eliminadas")

    for player_id, stats in PLAYER_STATS.items():
        surface_rates = SURFACE_WIN_RATES.get(player_id, {})
        db_stats = PlayerStatsDB(
            player_id=player_id,
            player_name=stats.player_name,
            overall_win_rate=stats.overall_win_rate,
            clay_win_rate=surface_rates.get("clay", 50.0),
            hard_win_rate=surface_rates.get("hard", 50.0),
            grass_win_rate=surface_rates.get("grass", 50.0),
            recent_form=json.dumps(stats.recent_form),
            recent_win_rate=stats.recent_win_rate,
            total_matches=stats.total_matches,
            titles=stats.titles,
        )
        session.add(db_stats)

    await session.commit()
    print(f"✅ {len(PLAYER_STATS)} estadísticas de jugadores insertadas")


async def seed_head_to_head(session, clean=False):
    if clean:
        await session.execute(delete(HeadToHeadDB))
        print("🗑️  Head-to-Head eliminados")

    for (p1, p2), h2h in H2H_DATA.items():
        db_h2h = HeadToHeadDB(
            player1_id=p1,
            player2_id=p2,
            player1_wins=h2h.player1_wins,
            player2_wins=h2h.player2_wins,
            total_matches=h2h.total_matches,
            last_matches=json.dumps([m.model_dump() for m in h2h.last_matches]),
        )
        session.add(db_h2h)

    await session.commit()
    print(f"✅ {len(H2H_DATA)} registros H2H insertados")


async def main():
    clean = "--clean" in sys.argv

    print("🌱 Iniciando seed de OddsEngine...")
    print(f"   Modo: {'limpio (--clean)' if clean else 'incremental'}")
    print()

    await create_tables()
    print("📋 Tablas verificadas/creadas")

    async with AsyncSessionLocal() as session:
        await seed_matches(session, clean)
        await seed_player_stats(session, clean)
        await seed_head_to_head(session, clean)

    print()
    print("🎾 Seed completado exitosamente!")


if __name__ == "__main__":
    asyncio.run(main())

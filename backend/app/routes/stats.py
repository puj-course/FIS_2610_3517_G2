"""
Endpoints REST para estadísticas de partidos.
"""

import logging
from fastapi import APIRouter

from app.services.stats_service import get_stats_service
from app.models.stats import MatchStats

logger = logging.getLogger("oddsengine")

router = APIRouter(tags=["Estadísticas"])


@router.get("/matches/{match_id}/stats", response_model=MatchStats)
async def get_match_stats(match_id: str):
    """
    Obtener estadísticas completas de un partido.

    Incluye: stats de ambos jugadores, Head-to-Head y superficie.
    """
    service = get_stats_service()
    stats = await service.get_match_stats(match_id)
    logger.info(f"GET /matches/{match_id}/stats — retornando estadísticas")
    return stats

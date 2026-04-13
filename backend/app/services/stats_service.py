"""
Servicio de estadísticas de partidos.

Obtiene y procesa estadísticas para un partido dado,
incluyendo stats de ambos jugadores y Head-to-Head.
"""

import logging
from typing import Optional

from app.models.stats import MatchStats
from app.core.exceptions import NotFoundException

logger = logging.getLogger("oddsengine")


class StatsService:
    """Servicio de negocio para estadísticas de partidos."""

    def __init__(self):
        # Importación lazy para evitar circular import
        from app.providers.mock_stats_provider import MockStatsProvider
        self._provider = MockStatsProvider()

    def get_match_stats(self, match_id: str) -> MatchStats:
        """Obtener estadísticas completas de un partido."""
        stats = self._provider.get_match_stats(match_id)

        if stats is None:
            raise NotFoundException(f"Estadísticas no encontradas para partido {match_id}")

        logger.info(f"Stats obtenidas para partido {match_id}")
        return stats


# Singleton
_stats_service = None


def get_stats_service() -> StatsService:
    global _stats_service
    if _stats_service is None:
        _stats_service = StatsService()
    return _stats_service

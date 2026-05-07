"""
Servicio de estadísticas.
"""
import logging
from app.models.stats import MatchStats
from app.providers.mock_stats_provider import MockStatsProvider
from app.core.exceptions import NotFoundException

logger = logging.getLogger("oddsengine")


class StatsService:
    def __init__(self):
        self._provider = MockStatsProvider()

    async def get_match_stats(self, match_id: str) -> MatchStats:
        stats = await self._provider.get_match_stats(match_id)
        if stats is None:
            raise NotFoundException(resource="Estadísticas del partido", resource_id=match_id)
        return stats


_stats_service = None


def get_stats_service() -> StatsService:
    global _stats_service
    if _stats_service is None:
        _stats_service = StatsService()
    return _stats_service

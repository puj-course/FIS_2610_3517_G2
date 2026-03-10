"""
Servicio de partidos de tenis.

Soporta dos modos:
- "mock": lee datos del MockMatchProvider (desarrollo sin BD)
- "database": lee datos de PostgreSQL

El modo se configura en config.py con data_mode.
"""

import logging
from typing import Optional

from app.models.match import Match, MatchStatus
from app.providers.mock_provider import MockMatchProvider
from app.core.config import get_settings

logger = logging.getLogger("oddsengine")


class MatchService:
    """Servicio de negocio para consulta de partidos."""

    def __init__(self):
        self._provider = MockMatchProvider()
        self._settings = get_settings()

    def get_matches(
        self, status: Optional[str] = None, tournament: Optional[str] = None
    ) -> list[Match]:
        """
        Obtener partidos con filtros opcionales.
        Usa mock provider (modo por defecto para desarrollo).
        """
        # Validar status si se proporciona
        if status:
            valid = [s.value for s in MatchStatus]
            if status not in valid:
                from app.core.exceptions import ValidationException
                raise ValidationException(
                    f"Status '{status}' no válido. Opciones: {', '.join(valid)}"
                )

        matches = self._provider.get_matches()

        # Filtrar por status
        if status:
            matches = [m for m in matches if m.status.value == status]

        # Filtrar por torneo
        if tournament:
            matches = [
                m for m in matches
                if tournament.lower() in m.tournament.name.lower()
            ]

        # Ordenar por fecha
        matches.sort(key=lambda m: m.date)

        logger.info(f"Retornando {len(matches)} partidos")
        return matches

    def get_match_by_id(self, match_id: str) -> Optional[Match]:
        """Obtener un partido por ID."""
        return self._provider.get_match_by_id(match_id)


# Singleton
_service = None


def get_match_service() -> MatchService:
    global _service
    if _service is None:
        _service = MatchService()
    return _service

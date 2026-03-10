from abc import ABC, abstractmethod
from typing import Optional

from app.models.match import Match, MatchStatus


class BaseMatchProvider(ABC):
    """Interfaz abstracta para proveedores de datos de partidos."""

    @abstractmethod
    async def get_matches(
        self,
        status: Optional[MatchStatus] = None,
        tournament: Optional[str] = None,
    ) -> list[Match]:
        """Obtiene la lista de partidos, opcionalmente filtrada."""
        ...

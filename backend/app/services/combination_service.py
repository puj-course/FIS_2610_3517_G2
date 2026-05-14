"""
Servicio de negocio para gestión de combinadas de apuestas.

Responsabilidades:
- Crear combinadas
- Agregar partidos (con validación de duplicados)
- Eliminar partidos
- Consultar combinada activa
- Validar que los partidos existan antes de agregarlos
"""

import logging
from datetime import datetime
from typing import Optional

from app.models.combination import (
    Combination,
    Selection,
    CombinationResponse,
)
from app.models.match import Match
from app.core.storage import get_storage, InMemoryStorage
from app.core.exceptions import (
    NotFoundException,
    DuplicateException,
    ValidationException,
)
from app.services.match_service import get_match_service

logger = logging.getLogger("oddsengine")


class CombinationService:
    """Servicio para administrar combinadas de apuestas."""

    def __init__(self, storage: Optional[InMemoryStorage] = None):
        self._storage = storage or get_storage()

    async def create_combination(self) -> Combination:
        """Crea una nueva combinada vacía."""
        combination = Combination()
        self._storage.save_combination(combination)
        logger.info(f"Combinada creada: {combination.id}")
        return combination

    async def get_combination(self, combination_id: str) -> Combination:
        """Obtiene una combinada por su ID."""
        combination = self._storage.get_combination(combination_id)
        if not combination:
            raise NotFoundException(resource="Combinada", resource_id=combination_id)
        return combination

    async def add_match_to_combination(
        self, combination_id: str, match_id: str
    ) -> CombinationResponse:
        """
        Agrega un partido a una combinada existente.

        Validaciones:
        - La combinada debe existir
        - El partido debe existir en el sistema
        - El partido no debe estar duplicado en la combinada
        """
        # Validar que la combinada existe
        combination = await self.get_combination(combination_id)

        # Validar duplicado
        if combination.has_match(match_id):
            raise DuplicateException(
                message=f"El partido '{match_id}' ya está en la combinada"
            )

        # Validar que el partido existe
        match_service = get_match_service()
        match = await match_service.get_match_by_id(match_id)
        if not match:
            raise NotFoundException(resource="Partido", resource_id=match_id)

        # Crear selección con datos del partido
        selection = Selection(
            match_id=match.id,
            player_home_name=match.player_home.name,
            player_away_name=match.player_away.name,
            tournament_name=match.tournament.name,
            match_date=match.date,
        )

        # Agregar a la combinada
        combination.selections.append(selection)
        combination.updated_at = datetime.now()
        self._storage.save_combination(combination)

        logger.info(
            f"Partido {match_id} agregado a combinada {combination_id} "
            f"(total: {combination.total_selections})"
        )

        return CombinationResponse(
            id=combination.id,
            selections=combination.selections,
            total_selections=combination.total_selections,
            created_at=combination.created_at,
            updated_at=combination.updated_at,
            message=f"Partido agregado correctamente. Total: {combination.total_selections} selecciones.",
        )

    async def remove_match_from_combination(
        self, combination_id: str, match_id: str
    ) -> CombinationResponse:
        """
        Elimina un partido de una combinada.

        Validaciones:
        - La combinada debe existir
        - El partido debe estar en la combinada
        """
        combination = await self.get_combination(combination_id)

        # Buscar la selección
        selection = combination.get_selection_by_match(match_id)
        if not selection:
            raise NotFoundException(
                resource="Selección del partido",
                resource_id=match_id,
            )

        # Eliminar
        combination.selections = [
            s for s in combination.selections if s.match_id != match_id
        ]
        combination.updated_at = datetime.now()
        self._storage.save_combination(combination)

        logger.info(
            f"Partido {match_id} eliminado de combinada {combination_id} "
            f"(total: {combination.total_selections})"
        )

        return CombinationResponse(
            id=combination.id,
            selections=combination.selections,
            total_selections=combination.total_selections,
            created_at=combination.created_at,
            updated_at=combination.updated_at,
            message=f"Partido eliminado correctamente. Total: {combination.total_selections} selecciones.",
        )

    async def delete_combination(self, combination_id: str) -> bool:
        """Elimina una combinada completa."""
        # Verificar que existe
        await self.get_combination(combination_id)

        deleted = self._storage.delete_combination(combination_id)
        logger.info(f"Combinada {combination_id} eliminada")
        return deleted

    async def list_combinations(self) -> list[Combination]:
        """Lista todas las combinadas activas."""
        return self._storage.list_combinations()


# Singleton
_combination_service: Optional[CombinationService] = None


def get_combination_service() -> CombinationService:
    global _combination_service
    if _combination_service is None:
        _combination_service = CombinationService()
    return _combination_service

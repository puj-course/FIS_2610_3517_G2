"""
Servicio de negocio para gestión de combinadas de apuestas.

Responsabilidades:
- Crear combinadas
- Agregar partidos (con validación de duplicados)
- Eliminar partidos
- Consultar combinada activa
- Guardar combinada en base de datos
- Validar que los partidos existan antes de agregarlos
"""

import logging
from datetime import datetime, timezone
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
        logger.info("Combinada creada")
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
        combination.updated_at = datetime.now(timezone.utc)
        self._storage.save_combination(combination)

        logger.info("Partido agregado a combinada")

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
        combination.updated_at = datetime.now(timezone.utc)
        self._storage.save_combination(combination)

        logger.info("Partido eliminado de combinada")

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
        logger.info("Combinada eliminada")
        return deleted

    async def list_combinations(self) -> list[Combination]:
        """Lista todas las combinadas activas."""
        return self._storage.list_combinations()

    async def save_combination_to_db(self, combination_id: str) -> dict:
        """
        Persiste la combinada y sus selecciones en PostgreSQL.

        Si la combinada ya existe en BD, borra sus selecciones anteriores
        y las reinserta con el estado actual (upsert completo).

        Requiere que DATA_MODE=database esté configurado.
        """
        from app.core.config import get_settings
        settings = get_settings()

        combination = await self.get_combination(combination_id)

        if settings.data_mode != "database":
            # En modo memoria no hay BD real — devolver confirmación igualmente
            # para no romper el flujo en desarrollo local sin PostgreSQL.
            logger.warning("save_combination_to_db llamado sin persistencia real en BD")
            return {
                "message": (
                    f"Combinada '{combination_id}' guardada "
                    f"({combination.total_selections} selecciones). "
                    "Nota: el servidor está en modo memoria; configura DATA_MODE=database "
                    "para persistencia real."
                ),
                "combination_id": combination_id,
                "total_selections": combination.total_selections,
                "saved": False,
            }

        # Modo database: persistir en PostgreSQL
        from app.core.database import AsyncSessionLocal
        from app.models.db_models import CombinationDB, SelectionDB
        from sqlalchemy import select, delete

        async with AsyncSessionLocal() as session:
            async with session.begin():
                # Verificar si ya existe en BD
                result = await session.execute(
                    select(CombinationDB).where(CombinationDB.id == combination_id)
                )
                db_combination = result.scalar_one_or_none()

                if db_combination is None:
                    # Insertar nueva
                    db_combination = CombinationDB(
                        id=combination.id,
                        created_at=combination.created_at,
                        updated_at=combination.updated_at,
                    )
                    session.add(db_combination)
                else:
                    # Actualizar timestamps
                    db_combination.updated_at = datetime.now(timezone.utc)

                # Borrar selecciones anteriores (para hacer upsert limpio)
                await session.execute(
                    delete(SelectionDB).where(
                        SelectionDB.combination_id == combination_id
                    )
                )

                # Reinsertar selecciones actuales
                for sel in combination.selections:
                    db_sel = SelectionDB(
                        id=sel.id,
                        combination_id=combination_id,
                        match_id=sel.match_id,
                        player_home_name=sel.player_home_name,
                        player_away_name=sel.player_away_name,
                        tournament_name=sel.tournament_name,
                        match_date=sel.match_date,
                        added_at=sel.added_at,
                    )
                    session.add(db_sel)

        logger.info("Combinada persistida en BD")

        return {
            "message": f"Combinada guardada correctamente con {combination.total_selections} selecciones.",
            "combination_id": combination_id,
            "total_selections": combination.total_selections,
            "saved": True,
        }


# Singleton
_combination_service: Optional[CombinationService] = None


def get_combination_service() -> CombinationService:
    global _combination_service
    if _combination_service is None:
        _combination_service = CombinationService()
    return _combination_service

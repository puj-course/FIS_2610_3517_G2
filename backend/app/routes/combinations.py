"""
Rutas de combinadas de apuestas.

Endpoints:
    POST   /api/combinations                              — Crear combinada
    GET    /api/combinations                              — Listar combinadas
    GET    /api/combinations/{id}                         — Consultar combinada
    DELETE /api/combinations/{id}                         — Eliminar combinada
    POST   /api/combinations/{id}/matches                 — Agregar partido
    DELETE /api/combinations/{id}/matches/{match_id}      — Eliminar partido
    POST   /api/combinations/{id}/save                    — Guardar combinada en BD
"""

import logging
from fastapi import APIRouter

from app.models.combination import (
    Combination,
    SelectionRequest,
    CombinationResponse,
    CombinationSummary,
)
from app.services.combination_service import get_combination_service

logger = logging.getLogger("oddsengine")

router = APIRouter(prefix="/combinations", tags=["combinations"])


@router.post("", response_model=CombinationResponse, status_code=201)
async def create_combination():
    """
    Crea una nueva combinada de apuestas vacía.

    Retorna la combinada creada con su ID único para posteriores operaciones.
    """
    service = get_combination_service()
    combination = service.create_combination()
    logger.info("POST /combinations — combinada creada")

    return CombinationResponse(
        id=combination.id,
        selections=combination.selections,
        total_selections=combination.total_selections,
        created_at=combination.created_at,
        updated_at=combination.updated_at,
        message="Combinada creada exitosamente. Agregue partidos para comenzar.",
    )


@router.get("", response_model=list[CombinationSummary])
async def list_combinations():
    """Lista todas las combinadas activas."""
    service = get_combination_service()
    combinations = service.list_combinations()
    logger.info("GET /combinations — listado solicitado")

    return [
        CombinationSummary(
            id=c.id,
            total_selections=c.total_selections,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in combinations
    ]


@router.get("/{combination_id}", response_model=CombinationResponse)
async def get_combination(combination_id: str):
    """
    Consulta una combinada activa con todas sus selecciones.

    Retorna la lista de partidos seleccionados y el total.
    """
    service = get_combination_service()
    combination = service.get_combination(combination_id)
    logger.info("GET /combinations — consulta por ID")

    return CombinationResponse(
        id=combination.id,
        selections=combination.selections,
        total_selections=combination.total_selections,
        created_at=combination.created_at,
        updated_at=combination.updated_at,
    )


@router.delete("/{combination_id}", status_code=200)
async def delete_combination(combination_id: str):
    """Elimina una combinada completa."""
    service = get_combination_service()
    await service.delete_combination(combination_id)
    logger.info("DELETE /combinations — combinada eliminada")

    return {"message": f"Combinada '{combination_id}' eliminada correctamente"}


@router.post("/{combination_id}/matches", response_model=CombinationResponse)
async def add_match_to_combination(
    combination_id: str,
    request: SelectionRequest,
):
    """
    Agrega un partido a la combinada.

    Validaciones:
    - La combinada debe existir
    - El partido debe existir en el sistema
    - No se permiten duplicados (mismo partido dos veces)
    """
    service = get_combination_service()
    result = await service.add_match_to_combination(
        combination_id=combination_id,
        match_id=request.match_id,
    )
    logger.info("POST /combinations/matches — partido agregado")
    return result


@router.delete(
    "/{combination_id}/matches/{match_id}",
    response_model=CombinationResponse,
)
async def remove_match_from_combination(combination_id: str, match_id: str):
    """
    Elimina un partido de la combinada.

    Validaciones:
    - La combinada debe existir
    - El partido debe estar en la combinada
    """
    service = get_combination_service()
    result = await service.remove_match_from_combination(
        combination_id=combination_id,
        match_id=match_id,
    )
    logger.info("DELETE /combinations/matches — partido eliminado")
    return result


@router.post("/{combination_id}/save", status_code=200)
async def save_combination(combination_id: str):
    """
    Persiste la combinada activa en la base de datos (PostgreSQL).

    Guarda tanto la combinada como todas sus selecciones actuales.
    Si la combinada ya existía en BD, actualiza sus selecciones.
    """
    service = get_combination_service()
    result = await service.save_combination_to_db(combination_id)
    logger.info("POST /combinations/save — combinada guardada en BD")
    return result

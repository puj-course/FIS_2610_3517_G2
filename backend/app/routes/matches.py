"""
Rutas de partidos de tenis.

Endpoints:
    GET /api/matches          — Lista partidos con filtros opcionales
    GET /api/matches/{id}     — Obtiene un partido específico
"""

import logging
from fastapi import APIRouter, Query
from typing import Optional

from app.models.match import Match, MatchStatus
from app.services.match_service import get_match_service
from app.core.exceptions import NotFoundException

logger = logging.getLogger("oddsengine")

router = APIRouter(tags=["matches"])


@router.get("/matches", response_model=list[Match])
async def list_matches(
    status: Optional[MatchStatus] = Query(None, description="Filtrar por estado del partido"),
    tournament: Optional[str] = Query(None, description="Filtrar por nombre de torneo"),
    page: int = Query(1, description="Número de página (desde 1)"),
    limit: int = Query(10, description="Partidos por página"),
):
    """
    Lista los partidos de tenis disponibles.

    Soporta filtros opcionales por estado (upcoming, live, finished)
    y por nombre de torneo (búsqueda parcial).
    Soporta paginación con page y limit.
    """
    from app.core.exceptions import ValidationException

    if page < 1:
        raise ValidationException("El parámetro 'page' debe ser >= 1")
    if limit < 1:
        raise ValidationException("El parámetro 'limit' debe ser >= 1")

    logger.info("GET /matches — listado con filtros solicitado")
    service = get_match_service()
    matches = await service.get_matches(status=status, tournament=tournament)

    # Paginación: aplicar después de filtros
    start = (page - 1) * limit
    end = start + limit
    paginated = matches[start:end]

    logger.info("GET /matches — respuesta paginada enviada")
    return paginated


@router.get("/matches/{match_id}", response_model=Match)
async def get_match(match_id: str):
    """Obtiene un partido específico por su ID."""
    logger.info("GET /matches — consulta por ID")
    service = get_match_service()
    match = await service.get_match_by_id(match_id)
    if not match:
        raise NotFoundException(resource="Partido", resource_id=match_id)
    return match

"""
Endpoints REST para historial y exportar combinadas.
Sprint 9: Historial, completar, exportar
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter

from app.services.combination_service import get_combination_service
from app.services.probability_service import get_probability_service

logger = logging.getLogger("oddsengine")

router = APIRouter(tags=["Historial"])


@router.get("/combinations/history")
async def get_combinations_history():
    """
    Obtener historial de combinadas (activas y completadas).
    Ordenadas por fecha de creación (más reciente primero).
    """
    service = get_combination_service()
    combinations = service.list_combinations()
    return {
        "total": len(combinations),
        "combinations": combinations,
    }


@router.post("/combinations/{combination_id}/complete")
async def complete_combination(combination_id: str):
    """
    Completar una combinada (marcar como finalizada).
    Calcula y guarda el resultado final.
    """
    comb_service = get_combination_service()
    prob_service = get_probability_service()

    combination = await comb_service.get_combination(combination_id)

    # Calcular resultado final
    result = await prob_service.calculate_combination(combination_id)

    logger.info(
        f"Combinada {combination_id} completada — "
        f"Probabilidad: {result.total_probability}% ({result.risk_level.value})"
    )

    return {
        "message": f"Combinada completada con {result.total_matches} partidos",
        "combination_id": combination_id,
        "probability": result.total_probability,
        "risk_level": result.risk_level.value,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/combinations/{combination_id}/export")
async def export_combination(combination_id: str):
    """
    Exportar resultado completo de una combinada como JSON.
    Incluye todos los detalles para descarga.
    """
    comb_service = get_combination_service()
    prob_service = get_probability_service()

    combination = await comb_service.get_combination(combination_id)
    result = await prob_service.calculate_combination(combination_id)

    export_data = {
        "export_info": {
            "app": "OddsEngine",
            "version": "1.0.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
        },
        "combination": {
            "id": combination.id,
            "total_selections": combination.total_selections,
            "created_at": combination.created_at.isoformat() if combination.created_at else None,
        },
        "result": {
            "total_probability": result.total_probability,
            "risk_level": result.risk_level.value,
            "risk_message": result.message,
        },
        "matches": [
            {
                "match_id": m.match_id,
                "players": f"{m.player_home_name} vs {m.player_away_name}",
                "probability": m.probability,
                "favorite": m.favorite,
            }
            for m in result.matches_detail
        ],
    }

    logger.info(f"Exportada combinada {combination_id}")
    return export_data

"""
Endpoints REST para probabilidad individual y combinada.
Sprint 6: GET /matches/{id}/probability
Sprint 7: GET /combinations/{id}/probability, GET /combinations/{id}/result
"""

import logging
from fastapi import APIRouter

from app.services.probability_service import get_probability_service
from app.models.probability import IndividualProbability, CombinationProbability

logger = logging.getLogger("oddsengine")

router = APIRouter(tags=["Probabilidad"])


@router.get("/matches/{match_id}/probability", response_model=IndividualProbability)
async def get_match_probability(match_id: str):
    """
    Calcular probabilidad individual de un partido.

    Fórmula: 40% forma reciente + 30% H2H + 30% superficie.
    Retorna probabilidad de cada jugador con desglose de factores.
    """
    service = get_probability_service()
    result = service.calculate_individual(match_id)
    logger.info(f"GET /matches/{match_id}/probability — {result.player_home_probability}% vs {result.player_away_probability}%")
    return result


@router.get("/combinations/{combination_id}/probability", response_model=CombinationProbability)
async def get_combination_probability(combination_id: str):
    """
    Calcular probabilidad total de una combinada.

    Fórmula: P_total = P1 × P2 × ... × Pn
    Retorna probabilidad total con clasificación de riesgo.
    """
    service = get_probability_service()
    result = service.calculate_combination(combination_id)
    logger.info(f"GET /combinations/{combination_id}/probability — {result.total_probability}% ({result.risk_level.value})")
    return result


@router.get("/combinations/{combination_id}/result")
async def get_combination_result(combination_id: str):
    """
    Obtener resultado completo de una combinada.

    Incluye: probabilidad total, riesgo, desglose por partido, y mensaje.
    """
    service = get_probability_service()
    result = service.calculate_combination(combination_id)
    return {
        "combination_id": combination_id,
        "probability": result.total_probability,
        "risk_level": result.risk_level.value,
        "risk_message": result.message,
        "matches": [m.model_dump() for m in result.matches_detail],
        "total_matches": result.total_matches,
    }

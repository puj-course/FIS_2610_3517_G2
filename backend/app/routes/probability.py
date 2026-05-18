"""
Endpoints REST para probabilidad individual y combinada.
"""
import logging
from fastapi import APIRouter
from app.services.probability_service import get_probability_service
from app.models.probability import IndividualProbability, CombinationProbability

logger = logging.getLogger("oddsengine")
router = APIRouter(tags=["Probabilidad"])


@router.get("/matches/{match_id}/probability", response_model=IndividualProbability)
async def get_match_probability(match_id: str):
    service = get_probability_service()
    result = await service.calculate_individual(match_id)
    logger.info("GET /matches/probability — consulta realizada")
    return result


@router.get("/combinations/{combination_id}/probability", response_model=CombinationProbability)
async def get_combination_probability(combination_id: str):
    service = get_probability_service()
    result = await service.calculate_combination(combination_id)
    logger.info("GET /combinations/probability — consulta realizada")
    return result


@router.get("/combinations/{combination_id}/result")
async def get_combination_result(combination_id: str):
    service = get_probability_service()
    result = await service.calculate_combination(combination_id)
    return {
        "combination_id": combination_id,
        "probability": result.total_probability,
        "risk_level": result.risk_level.value,
        "risk_message": result.message,
        "matches": [m.model_dump() for m in result.matches_detail],
        "total_matches": result.total_matches,
    }

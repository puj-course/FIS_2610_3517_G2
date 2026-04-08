"""
Modelos de probabilidad para análisis de partidos y combinadas.
Sprint 6: Probabilidad individual
Sprint 7: Probabilidad combinada
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"       # > 50% → Riesgo bajo
    MEDIUM = "medium"  # 20-50% → Riesgo medio
    HIGH = "high"      # < 20% → Riesgo alto


class ProbabilityFactor(BaseModel):
    """Factor individual que contribuye al cálculo de probabilidad."""
    name: str
    weight: float = Field(ge=0, le=1, description="Peso del factor (0-1)")
    value: float = Field(ge=0, le=100, description="Valor del factor (0-100)")
    description: str = ""

    @property
    def weighted_value(self) -> float:
        return self.weight * self.value


class IndividualProbability(BaseModel):
    """Resultado del cálculo de probabilidad individual de un partido."""
    match_id: str
    player_home_name: str
    player_away_name: str
    player_home_probability: float = Field(ge=0, le=100)
    player_away_probability: float = Field(ge=0, le=100)
    factors_home: list[ProbabilityFactor] = Field(default_factory=list)
    factors_away: list[ProbabilityFactor] = Field(default_factory=list)
    confidence: str = "medium"  # "high", "medium", "low"
    message: str = ""

    def get_favorite(self) -> str:
        if self.player_home_probability > self.player_away_probability:
            return self.player_home_name
        return self.player_away_name


class MatchProbabilityDetail(BaseModel):
    """Probabilidad de un partido dentro de una combinada."""
    match_id: str
    player_home_name: str
    player_away_name: str
    probability: float = Field(ge=0, le=100)
    favorite: str


class CombinationProbability(BaseModel):
    """Resultado del cálculo de probabilidad de una combinada."""
    combination_id: str
    total_probability: float = Field(ge=0, le=100)
    risk_level: RiskLevel
    matches_detail: list[MatchProbabilityDetail] = Field(default_factory=list)
    total_matches: int
    message: str = ""

    @classmethod
    def classify_risk(cls, probability: float) -> RiskLevel:
        if probability > 50:
            return RiskLevel.LOW
        elif probability > 20:
            return RiskLevel.MEDIUM
        return RiskLevel.HIGH

    @classmethod
    def get_risk_message(cls, risk: RiskLevel) -> str:
        messages = {
            RiskLevel.LOW: "Combinada con riesgo bajo. Las probabilidades están a tu favor.",
            RiskLevel.MEDIUM: "Combinada con riesgo moderado. Considera revisar los partidos.",
            RiskLevel.HIGH: "Combinada con riesgo alto. Las probabilidades son bajas.",
        }
        return messages[risk]

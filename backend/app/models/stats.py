"""
Modelos Pydantic para estadísticas de jugadores y partidos.

Estos modelos representan la estructura de datos que la API retorna
para las visualizaciones de estadísticas en el frontend.
"""

from pydantic import BaseModel, Field
from typing import Optional


class PlayerStats(BaseModel):
    """Estadísticas de un jugador individual."""
    player_id: str
    player_name: str
    overall_win_rate: float = Field(ge=0, le=100, description="Win rate general (%)")
    surface_win_rate: float = Field(ge=0, le=100, description="Win rate en la superficie del torneo (%)")
    recent_form: list[str] = Field(default_factory=list, description="Últimos resultados: W o L")
    recent_win_rate: float = Field(ge=0, le=100, description="Win rate últimos partidos (%)")
    total_matches: int = Field(ge=0, description="Total de partidos jugados")
    titles: int = Field(ge=0, description="Títulos ganados")


class HeadToHeadMatch(BaseModel):
    """Resumen de un encuentro en el historial H2H."""
    date: str
    tournament: str
    winner: str
    score: str


class HeadToHead(BaseModel):
    """Historial de enfrentamientos directos entre dos jugadores."""
    player1_id: str
    player2_id: str
    player1_name: str
    player2_name: str
    player1_wins: int = Field(ge=0)
    player2_wins: int = Field(ge=0)
    total_matches: int = Field(ge=0)
    last_matches: list[HeadToHeadMatch] = Field(default_factory=list)


class MatchStats(BaseModel):
    """Estadísticas completas de un partido (ambos jugadores + H2H)."""
    match_id: str
    player_home_stats: PlayerStats
    player_away_stats: PlayerStats
    head_to_head: Optional[HeadToHead] = None
    surface: str

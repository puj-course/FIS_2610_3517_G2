"""
Modelos Pydantic para estadísticas de jugadores y partidos.
"""

from pydantic import BaseModel, Field
from typing import Optional


class PlayerStats(BaseModel):
    player_id: str
    player_name: str
    overall_win_rate: float = Field(ge=0, le=100, description="Win rate general (%)")
    surface_win_rate: float = Field(ge=0, le=100, description="Win rate en la superficie del torneo (%)")
    recent_form: list[str] = Field(default_factory=list, description="Últimos resultados: W o L")
    recent_win_rate: float = Field(ge=0, le=100, description="Win rate últimos partidos (%)")
    total_matches: int = Field(ge=0, description="Total de partidos jugados")
    titles: int = Field(ge=0, description="Títulos ganados")


class HeadToHeadMatch(BaseModel):
    date: str
    tournament: str
    winner: str
    score: str


class HeadToHead(BaseModel):
    player1_id: str
    player2_id: str
    player1_name: str
    player2_name: str
    player1_wins: int = Field(ge=0)
    player2_wins: int = Field(ge=0)
    total_matches: int = Field(ge=0)
    last_matches: list[HeadToHeadMatch] = Field(default_factory=list)


class MatchStats(BaseModel):
    match_id: str
    player_home_stats: PlayerStats
    player_away_stats: PlayerStats
    head_to_head: Optional[HeadToHead] = None
    surface: str

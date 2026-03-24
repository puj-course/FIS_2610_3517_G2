from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional


class MatchStatus(str, Enum):
    UPCOMING = "upcoming"
    LIVE = "live"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class Surface(str, Enum):
    HARD = "hard"
    CLAY = "clay"
    GRASS = "grass"
    CARPET = "carpet"


class Player(BaseModel):
    id: str
    name: str
    country: str
    ranking: Optional[int] = None


class Tournament(BaseModel):
    id: str
    name: str
    surface: Surface
    category: str  # "ATP", "WTA", "Grand Slam"
    location: str


class Match(BaseModel):
    id: str
    player_home: Player
    player_away: Player
    tournament: Tournament
    date: datetime
    status: MatchStatus
    score: Optional[str] = None  # ej: "6-3, 7-5"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "match_001",
                "player_home": {
                    "id": "p_001",
                    "name": "Carlos Alcaraz",
                    "country": "ESP",
                    "ranking": 2,
                },
                "player_away": {
                    "id": "p_002",
                    "name": "Jannik Sinner",
                    "country": "ITA",
                    "ranking": 1,
                },
                "tournament": {
                    "id": "t_001",
                    "name": "Roland Garros",
                    "surface": "clay",
                    "category": "Grand Slam",
                    "location": "Paris, France",
                },
                "date": "2026-05-25T14:00:00",
                "status": "upcoming",
                "score": None,
            }
        }

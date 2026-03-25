"""
Modelos de datos para combinadas de apuestas.

Una Combination agrupa múltiples Selection, donde cada Selection
representa un partido seleccionado por el usuario para su combinada.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import uuid4


class Selection(BaseModel):
    """
    Representa la selección de un partido dentro de una combinada.

    Cada selección vincula un match_id con metadata básica del partido
    para evitar consultas adicionales al visualizar la combinada.
    """
    id: str = Field(default_factory=lambda: f"sel_{uuid4().hex[:8]}")
    match_id: str
    player_home_name: str
    player_away_name: str
    tournament_name: str
    match_date: datetime
    added_at: datetime = Field(default_factory=datetime.now)


class SelectionRequest(BaseModel):
    """Datos requeridos para agregar un partido a la combinada."""
    match_id: str


class Combination(BaseModel):
    """
    Representa una combinada de apuestas activa.

    Agrupa múltiples selecciones y mantiene metadata de la sesión:
    fecha de creación, última modificación y conteo de partidos.
    """
    id: str = Field(default_factory=lambda: f"comb_{uuid4().hex[:8]}")
    selections: list[Selection] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def total_selections(self) -> int:
        """Número total de partidos en la combinada."""
        return len(self.selections)

    def has_match(self, match_id: str) -> bool:
        """Verifica si un partido ya está en la combinada."""
        return any(s.match_id == match_id for s in self.selections)

    def get_selection_by_match(self, match_id: str) -> Optional[Selection]:
        """Obtiene la selección asociada a un match_id."""
        for s in self.selections:
            if s.match_id == match_id:
                return s
        return None


class CombinationSummary(BaseModel):
    """Resumen de una combinada para respuestas de listado."""
    id: str
    total_selections: int
    created_at: datetime
    updated_at: datetime


class CombinationResponse(BaseModel):
    """Respuesta completa de una combinada con sus selecciones."""
    id: str
    selections: list[Selection]
    total_selections: int
    created_at: datetime
    updated_at: datetime
    message: str = ""

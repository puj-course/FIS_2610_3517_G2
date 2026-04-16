"""
Proveedor mock de estadísticas de jugadores.

Datos ficticios pero coherentes con el ranking real ATP.
Se usa para desarrollo sin depender de PostgreSQL o API externa.
"""

import json
from typing import Optional

from app.models.stats import PlayerStats, HeadToHead, HeadToHeadMatch, MatchStats


# Estadísticas por jugador (coherentes con ranking real)
PLAYER_STATS = {
    "p_001": PlayerStats(
        player_id="p_001", player_name="Carlos Alcaraz",
        overall_win_rate=76.5, surface_win_rate=0,  # se ajusta por superficie
        recent_form=["W", "W", "L", "W", "W", "W", "L", "W", "W", "W"],
        recent_win_rate=80.0, total_matches=185, titles=16,
    ),
    "p_002": PlayerStats(
        player_id="p_002", player_name="Jannik Sinner",
        overall_win_rate=78.2, surface_win_rate=0,
        recent_form=["W", "W", "W", "W", "L", "W", "W", "W", "L", "W"],
        recent_win_rate=80.0, total_matches=195, titles=18,
    ),
    "p_003": PlayerStats(
        player_id="p_003", player_name="Novak Djokovic",
        overall_win_rate=83.1, surface_win_rate=0,
        recent_form=["L", "W", "W", "L", "W", "L", "W", "W", "W", "L"],
        recent_win_rate=60.0, total_matches=1320, titles=99,
    ),
    "p_004": PlayerStats(
        player_id="p_004", player_name="Daniil Medvedev",
        overall_win_rate=66.8, surface_win_rate=0,
        recent_form=["W", "L", "W", "L", "W", "W", "L", "W", "L", "W"],
        recent_win_rate=60.0, total_matches=380, titles=20,
    ),
    "p_005": PlayerStats(
        player_id="p_005", player_name="Alexander Zverev",
        overall_win_rate=68.5, surface_win_rate=0,
        recent_form=["W", "W", "W", "L", "W", "L", "W", "W", "L", "W"],
        recent_win_rate=70.0, total_matches=450, titles=22,
    ),
    "p_006": PlayerStats(
        player_id="p_006", player_name="Casper Ruud",
        overall_win_rate=62.3, surface_win_rate=0,
        recent_form=["L", "W", "L", "W", "W", "L", "W", "L", "W", "W"],
        recent_win_rate=60.0, total_matches=280, titles=10,
    ),
    "p_007": PlayerStats(
        player_id="p_007", player_name="Holger Rune",
        overall_win_rate=60.1, surface_win_rate=0,
        recent_form=["W", "L", "W", "W", "L", "L", "W", "W", "L", "W"],
        recent_win_rate=60.0, total_matches=160, titles=6,
    ),
    "p_008": PlayerStats(
        player_id="p_008", player_name="Taylor Fritz",
        overall_win_rate=63.7, surface_win_rate=0,
        recent_form=["W", "W", "L", "W", "L", "W", "L", "W", "W", "L"],
        recent_win_rate=60.0, total_matches=350, titles=8,
    ),
    "p_009": PlayerStats(
        player_id="p_009", player_name="Alex de Minaur",
        overall_win_rate=61.2, surface_win_rate=0,
        recent_form=["L", "W", "W", "L", "W", "W", "L", "L", "W", "W"],
        recent_win_rate=60.0, total_matches=290, titles=7,
    ),
    "p_010": PlayerStats(
        player_id="p_010", player_name="Stefanos Tsitsipas",
        overall_win_rate=65.4, surface_win_rate=0,
        recent_form=["W", "L", "L", "W", "W", "L", "W", "L", "W", "L"],
        recent_win_rate=50.0, total_matches=380, titles=12,
    ),
}

# Win rates por superficie
SURFACE_WIN_RATES = {
    "p_001": {"clay": 80.2, "hard": 74.1, "grass": 78.0},  # Alcaraz
    "p_002": {"clay": 68.5, "hard": 82.3, "grass": 72.0},  # Sinner
    "p_003": {"clay": 78.0, "hard": 85.5, "grass": 84.2},  # Djokovic
    "p_004": {"clay": 55.2, "hard": 72.8, "grass": 58.0},  # Medvedev
    "p_005": {"clay": 65.3, "hard": 70.1, "grass": 62.0},  # Zverev
    "p_006": {"clay": 72.8, "hard": 55.4, "grass": 48.0},  # Ruud
    "p_007": {"clay": 58.5, "hard": 62.3, "grass": 55.0},  # Rune
    "p_008": {"clay": 50.2, "hard": 68.5, "grass": 65.0},  # Fritz
    "p_009": {"clay": 48.5, "hard": 64.2, "grass": 68.0},  # de Minaur
    "p_010": {"clay": 70.1, "hard": 63.5, "grass": 58.0},  # Tsitsipas
}

# Head-to-Head entre pares de jugadores
H2H_DATA = {
    ("p_001", "p_002"): HeadToHead(
        player1_id="p_001", player2_id="p_002",
        player1_name="Carlos Alcaraz", player2_name="Jannik Sinner",
        player1_wins=5, player2_wins=4, total_matches=9,
        last_matches=[
            HeadToHeadMatch(date="2026-01-20", tournament="Australian Open", winner="Jannik Sinner", score="6-3, 7-5, 6-4"),
            HeadToHeadMatch(date="2025-11-15", tournament="ATP Finals", winner="Carlos Alcaraz", score="6-4, 6-7, 6-3"),
            HeadToHeadMatch(date="2025-07-14", tournament="Wimbledon", winner="Carlos Alcaraz", score="7-6, 6-4, 7-6"),
        ]
    ),
    ("p_003", "p_004"): HeadToHead(
        player1_id="p_003", player2_id="p_004",
        player1_name="Novak Djokovic", player2_name="Daniil Medvedev",
        player1_wins=12, player2_wins=5, total_matches=17,
        last_matches=[
            HeadToHeadMatch(date="2025-09-08", tournament="US Open", winner="Novak Djokovic", score="6-3, 6-4, 6-2"),
            HeadToHeadMatch(date="2025-06-10", tournament="Roland Garros", winner="Daniil Medvedev", score="7-5, 6-4, 6-3"),
            HeadToHeadMatch(date="2025-03-15", tournament="Indian Wells", winner="Novak Djokovic", score="6-4, 7-6"),
        ]
    ),
    ("p_005", "p_006"): HeadToHead(
        player1_id="p_005", player2_id="p_006",
        player1_name="Alexander Zverev", player2_name="Casper Ruud",
        player1_wins=7, player2_wins=3, total_matches=10,
        last_matches=[
            HeadToHeadMatch(date="2025-10-05", tournament="Beijing", winner="Alexander Zverev", score="6-3, 6-4"),
            HeadToHeadMatch(date="2025-05-12", tournament="Madrid Open", winner="Alexander Zverev", score="7-6, 6-3"),
            HeadToHeadMatch(date="2025-04-20", tournament="Monte Carlo", winner="Casper Ruud", score="6-4, 7-5"),
        ]
    ),
    ("p_007", "p_008"): HeadToHead(
        player1_id="p_007", player2_id="p_008",
        player1_name="Holger Rune", player2_name="Taylor Fritz",
        player1_wins=2, player2_wins=3, total_matches=5,
        last_matches=[
            HeadToHeadMatch(date="2025-08-20", tournament="Cincinnati", winner="Taylor Fritz", score="6-4, 6-3"),
            HeadToHeadMatch(date="2025-06-28", tournament="Wimbledon", winner="Holger Rune", score="7-6, 3-6, 6-4, 6-3"),
        ]
    ),
    ("p_009", "p_010"): HeadToHead(
        player1_id="p_009", player2_id="p_010",
        player1_name="Alex de Minaur", player2_name="Stefanos Tsitsipas",
        player1_wins=3, player2_wins=6, total_matches=9,
        last_matches=[
            HeadToHeadMatch(date="2025-11-10", tournament="Paris Masters", winner="Stefanos Tsitsipas", score="6-3, 7-5"),
            HeadToHeadMatch(date="2025-07-02", tournament="Wimbledon", winner="Alex de Minaur", score="6-4, 3-6, 7-6, 6-2"),
        ]
    ),
}


class MockStatsProvider:
    """Proveedor mock de estadísticas para desarrollo."""

    def get_player_stats(self, player_id: str, surface: str = "hard") -> Optional[PlayerStats]:
        """Obtener estadísticas de un jugador, ajustadas por superficie."""
        stats = PLAYER_STATS.get(player_id)
        if stats is None:
            return None

        # Crear copia con surface_win_rate ajustado
        surface_rates = SURFACE_WIN_RATES.get(player_id, {})
        surface_wr = surface_rates.get(surface, stats.overall_win_rate)

        return PlayerStats(
            player_id=stats.player_id,
            player_name=stats.player_name,
            overall_win_rate=stats.overall_win_rate,
            surface_win_rate=surface_wr,
            recent_form=stats.recent_form,
            recent_win_rate=stats.recent_win_rate,
            total_matches=stats.total_matches,
            titles=stats.titles,
        )

    def get_head_to_head(self, player1_id: str, player2_id: str) -> Optional[HeadToHead]:
        """Obtener H2H entre dos jugadores."""
        # Buscar en ambas direcciones
        h2h = H2H_DATA.get((player1_id, player2_id))
        if h2h:
            return h2h

        # Buscar invertido
        h2h = H2H_DATA.get((player2_id, player1_id))
        if h2h:
            # Invertir para que player1 sea el solicitado
            return HeadToHead(
                player1_id=player1_id,
                player2_id=player2_id,
                player1_name=h2h.player2_name,
                player2_name=h2h.player1_name,
                player1_wins=h2h.player2_wins,
                player2_wins=h2h.player1_wins,
                total_matches=h2h.total_matches,
                last_matches=h2h.last_matches,
            )

        return None

    async def get_match_stats(self, match_id: str) -> Optional[MatchStats]:
        """Obtener estadísticas completas para un partido."""
        from app.services.match_service import get_match_service
        match_service = get_match_service()
        match = await match_service.get_match_by_id(match_id)

        if match is None:
            return None

        surface = match.tournament.surface.value
        home_stats = self.get_player_stats(match.player_home.id, surface)
        away_stats = self.get_player_stats(match.player_away.id, surface)

        if home_stats is None or away_stats is None:
            return None

        h2h = self.get_head_to_head(match.player_home.id, match.player_away.id)

        return MatchStats(
            match_id=match_id,
            player_home_stats=home_stats,
            player_away_stats=away_stats,
            head_to_head=h2h,
            surface=surface,
        )

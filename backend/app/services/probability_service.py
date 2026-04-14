"""
Servicio de cálculo de probabilidad.
"""

import logging

from app.models.probability import (
    IndividualProbability, ProbabilityFactor,
    CombinationProbability, MatchProbabilityDetail, RiskLevel,
)
from app.models.stats import MatchStats
from app.core.exceptions import NotFoundException

logger = logging.getLogger("oddsengine")

WEIGHT_RECENT_FORM = 0.40
WEIGHT_H2H = 0.30
WEIGHT_SURFACE = 0.30


class ProbabilityService:

    def calculate_individual(self, match_id: str) -> IndividualProbability:
        from app.services.stats_service import get_stats_service
        from app.services.match_service import get_match_service

        match_service = get_match_service()
        stats_service = get_stats_service()

        match = match_service.get_match_by_id(match_id)
        if match is None:
            raise NotFoundException(f"Partido {match_id} no encontrado")

        try:
            stats = stats_service.get_match_stats(match_id)
        except NotFoundException:
            return IndividualProbability(
                match_id=match_id,
                player_home_name=match.player_home.name,
                player_away_name=match.player_away.name,
                player_home_probability=50.0,
                player_away_probability=50.0,
                confidence="low",
                message="Sin datos suficientes. Probabilidad estimada 50/50.",
            )

        home_score, home_factors = self._calculate_score(stats, is_home=True)
        away_score, away_factors = self._calculate_score(stats, is_home=False)

        total = home_score + away_score
        if total == 0:
            home_prob, away_prob = 50.0, 50.0
        else:
            home_prob = round((home_score / total) * 100, 1)
            away_prob = round(100 - home_prob, 1)

        confidence = self._determine_confidence(stats)

        return IndividualProbability(
            match_id=match_id,
            player_home_name=match.player_home.name,
            player_away_name=match.player_away.name,
            player_home_probability=home_prob,
            player_away_probability=away_prob,
            factors_home=home_factors,
            factors_away=away_factors,
            confidence=confidence,
            message=self._generate_message(match.player_home.name, home_prob,
                                           match.player_away.name, away_prob),
        )

    def calculate_combination(self, combination_id: str) -> CombinationProbability:
        from app.services.combination_service import get_combination_service

        comb_service = get_combination_service()
        combination = comb_service.get_combination(combination_id)

        if combination.total_selections < 2:
            return CombinationProbability(
                combination_id=combination_id,
                total_probability=0,
                risk_level=RiskLevel.HIGH,
                total_matches=combination.total_selections,
                message="Se necesitan al menos 2 partidos para calcular la combinada.",
            )

        matches_detail = []
        total_prob = 1.0

        for sel in combination.selections:
            try:
                indiv = self.calculate_individual(sel.match_id)
                prob = max(indiv.player_home_probability, indiv.player_away_probability)
                favorite = indiv.get_favorite()
            except Exception:
                prob = 50.0
                favorite = "N/A"

            matches_detail.append(MatchProbabilityDetail(
                match_id=sel.match_id,
                player_home_name=sel.player_home_name,
                player_away_name=sel.player_away_name,
                probability=prob,
                favorite=favorite,
            ))
            total_prob *= (prob / 100)

        total_prob_pct = round(total_prob * 100, 2)
        risk = CombinationProbability.classify_risk(total_prob_pct)

        return CombinationProbability(
            combination_id=combination_id,
            total_probability=total_prob_pct,
            risk_level=risk,
            matches_detail=matches_detail,
            total_matches=len(matches_detail),
            message=CombinationProbability.get_risk_message(risk),
        )

    def _calculate_score(self, stats: MatchStats, is_home: bool) -> tuple:
        player_stats = stats.player_home_stats if is_home else stats.player_away_stats
        factors = []

        recent_wr = player_stats.recent_win_rate
        factors.append(ProbabilityFactor(
            name="Forma reciente", weight=WEIGHT_RECENT_FORM, value=recent_wr,
            description=f"Win rate últimos partidos: {recent_wr}%",
        ))

        h2h_value = 50.0
        if stats.head_to_head:
            h2h = stats.head_to_head
            total = h2h.player1_wins + h2h.player2_wins
            if is_home:
                h2h_value = (h2h.player1_wins / total * 100) if total > 0 else 50.0
            else:
                h2h_value = (h2h.player2_wins / total * 100) if total > 0 else 50.0

        factors.append(ProbabilityFactor(
            name="Head-to-Head", weight=WEIGHT_H2H, value=round(h2h_value, 1),
            description=f"Historial directo: {round(h2h_value, 1)}% victorias",
        ))

        surface_wr = player_stats.surface_win_rate
        factors.append(ProbabilityFactor(
            name="Superficie", weight=WEIGHT_SURFACE, value=surface_wr,
            description=f"Win rate en {stats.surface}: {surface_wr}%",
        ))

        return sum(f.weighted_value for f in factors), factors

    def _determine_confidence(self, stats: MatchStats) -> str:
        has_h2h = stats.head_to_head is not None
        has_form = len(stats.player_home_stats.recent_form) >= 5
        has_surface = stats.player_home_stats.surface_win_rate > 0
        if has_h2h and has_form and has_surface:
            return "high"
        elif has_form or has_surface:
            return "medium"
        return "low"

    def _generate_message(self, home_name, home_prob, away_name, away_prob) -> str:
        diff = abs(home_prob - away_prob)
        if diff < 5:
            return f"Partido muy parejo entre {home_name} y {away_name}."
        elif diff < 15:
            favorite = home_name if home_prob > away_prob else away_name
            return f"{favorite} tiene una ligera ventaja en este partido."
        else:
            favorite = home_name if home_prob > away_prob else away_name
            return f"{favorite} es claro favorito en este partido."


_prob_service = None

def get_probability_service() -> ProbabilityService:
    global _prob_service
    if _prob_service is None:
        _prob_service = ProbabilityService()
    return _prob_service

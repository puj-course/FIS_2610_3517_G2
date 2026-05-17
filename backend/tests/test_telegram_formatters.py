import pytest
from datetime import datetime

from app.models.match import Match, Player, Tournament, MatchStatus, Surface
from app.telegram.formatters import (
    format_match_summary,
    format_match_detail,
    format_match_list,
    format_health,
)


def _make_match(
    match_id="match_001",
    home_name="Carlos Alcaraz",
    away_name="Jannik Sinner",
    status=MatchStatus.UPCOMING,
    score=None,
):
    return Match(
        id=match_id,
        player_home=Player(id="p1", name=home_name, country="ESP", ranking=2),
        player_away=Player(id="p2", name=away_name, country="ITA", ranking=1),
        tournament=Tournament(
            id="t1",
            name="Roland Garros",
            surface=Surface.CLAY,
            category="Grand Slam",
            location="Paris, France",
        ),
        date=datetime(2026, 5, 25, 14, 0),
        status=status,
        score=score,
    )


class TestFormatMatchSummary:
    def test_contains_player_names(self):
        result = format_match_summary(_make_match())
        assert "Carlos Alcaraz" in result
        assert "Jannik Sinner" in result

    def test_contains_tournament(self):
        result = format_match_summary(_make_match())
        assert "Roland Garros" in result

    def test_contains_status_label(self):
        result = format_match_summary(_make_match(status=MatchStatus.LIVE))
        assert "EN VIVO" in result

    def test_contains_score_when_present(self):
        result = format_match_summary(_make_match(score="6-3, 7-5"))
        assert "6-3, 7-5" in result

    def test_no_score_line_when_absent(self):
        result = format_match_summary(_make_match(score=None))
        assert "Score" not in result


class TestFormatMatchDetail:
    def test_contains_match_id(self):
        result = format_match_detail(_make_match(match_id="match_042"))
        assert "match_042" in result

    def test_contains_player_details(self):
        result = format_match_detail(_make_match())
        assert "ESP" in result
        assert "#2" in result
        assert "ITA" in result
        assert "#1" in result

    def test_contains_tournament_info(self):
        result = format_match_detail(_make_match())
        assert "Roland Garros" in result
        assert "clay" in result
        assert "Grand Slam" in result
        assert "Paris, France" in result

    def test_contains_date(self):
        result = format_match_detail(_make_match())
        assert "2026-05-25 14:00" in result

    def test_shows_score_for_finished(self):
        result = format_match_detail(
            _make_match(status=MatchStatus.FINISHED, score="6-3, 7-5")
        )
        assert "6-3, 7-5" in result
        assert "Finalizado" in result

    def test_no_ranking_shows_sr(self):
        match = _make_match()
        match.player_home.ranking = None
        result = format_match_detail(match)
        assert "S/R" in result


class TestFormatMatchList:
    def test_empty_list(self):
        result = format_match_list([], 0)
        assert "No se encontraron partidos" in result

    def test_single_match(self):
        matches = [_make_match()]
        result = format_match_list(matches, 1)
        assert "1 encontrado" in result
        assert "Carlos Alcaraz" in result

    def test_truncation_message(self):
        matches = [_make_match(match_id=f"m_{i}") for i in range(5)]
        result = format_match_list(matches, 20)
        assert "Mostrando 5 de 20" in result

    def test_no_truncation_message_when_all_shown(self):
        matches = [_make_match()]
        result = format_match_list(matches, 1)
        assert "Mostrando" not in result


class TestFormatHealth:
    def test_contains_all_fields(self):
        result = format_health(status="ok", version="1.0.0", data_mode="mock")
        assert "ok" in result
        assert "1.0.0" in result
        assert "mock" in result

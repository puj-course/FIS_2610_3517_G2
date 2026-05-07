from datetime import datetime, timedelta
from typing import Optional

from app.models.match import Match, Player, Tournament, MatchStatus, Surface
from app.providers.base import BaseMatchProvider


class MockMatchProvider(BaseMatchProvider):
    """Proveedor de datos mock para desarrollo y testing."""

    def __init__(self):
        self._matches = self._generate_mock_data()

    def _generate_mock_data(self) -> list[Match]:
        now = datetime.now()

        players = {
            "sinner": Player(id="p_001", name="Jannik Sinner", country="ITA", ranking=1),
            "alcaraz": Player(id="p_002", name="Carlos Alcaraz", country="ESP", ranking=2),
            "djokovic": Player(id="p_003", name="Novak Djokovic", country="SRB", ranking=3),
            "medvedev": Player(id="p_004", name="Daniil Medvedev", country="RUS", ranking=4),
            "zverev": Player(id="p_005", name="Alexander Zverev", country="GER", ranking=5),
            "rublev": Player(id="p_006", name="Andrey Rublev", country="RUS", ranking=6),
            "ruud": Player(id="p_007", name="Casper Ruud", country="NOR", ranking=7),
            "tsitsipas": Player(id="p_008", name="Stefanos Tsitsipas", country="GRE", ranking=8),
            "fritz": Player(id="p_009", name="Taylor Fritz", country="USA", ranking=9),
            "hurkacz": Player(id="p_010", name="Hubert Hurkacz", country="POL", ranking=10),
        }

        tournaments = {
            "rg": Tournament(
                id="t_001", name="Roland Garros", surface=Surface.CLAY,
                category="Grand Slam", location="Paris, France",
            ),
            "wimbledon": Tournament(
                id="t_002", name="Wimbledon", surface=Surface.GRASS,
                category="Grand Slam", location="London, UK",
            ),
            "madrid": Tournament(
                id="t_003", name="Madrid Open", surface=Surface.CLAY,
                category="ATP 1000", location="Madrid, Spain",
            ),
            "uso": Tournament(
                id="t_004", name="US Open", surface=Surface.HARD,
                category="Grand Slam", location="New York, USA",
            ),
        }

        return [
            Match(
                id="match_001",
                player_home=players["alcaraz"],
                player_away=players["sinner"],
                tournament=tournaments["rg"],
                date=now + timedelta(days=2, hours=3),
                status=MatchStatus.UPCOMING,
            ),
            Match(
                id="match_002",
                player_home=players["djokovic"],
                player_away=players["medvedev"],
                tournament=tournaments["rg"],
                date=now + timedelta(days=2, hours=5),
                status=MatchStatus.UPCOMING,
            ),
            Match(
                id="match_003",
                player_home=players["zverev"],
                player_away=players["ruud"],
                tournament=tournaments["rg"],
                date=now + timedelta(days=3),
                status=MatchStatus.UPCOMING,
            ),
            Match(
                id="match_004",
                player_home=players["tsitsipas"],
                player_away=players["rublev"],
                tournament=tournaments["madrid"],
                date=now - timedelta(hours=2),
                status=MatchStatus.LIVE,
                score="6-4, 3-2",
            ),
            Match(
                id="match_005",
                player_home=players["fritz"],
                player_away=players["hurkacz"],
                tournament=tournaments["madrid"],
                date=now - timedelta(days=1),
                status=MatchStatus.FINISHED,
                score="7-6(4), 6-3",
            ),
            Match(
                id="match_006",
                player_home=players["sinner"],
                player_away=players["zverev"],
                tournament=tournaments["madrid"],
                date=now - timedelta(days=1, hours=3),
                status=MatchStatus.FINISHED,
                score="6-4, 3-6, 7-5",
            ),
            Match(
                id="match_007",
                player_home=players["alcaraz"],
                player_away=players["djokovic"],
                tournament=tournaments["wimbledon"],
                date=now + timedelta(days=30),
                status=MatchStatus.UPCOMING,
            ),
            Match(
                id="match_008",
                player_home=players["medvedev"],
                player_away=players["fritz"],
                tournament=tournaments["uso"],
                date=now + timedelta(days=60),
                status=MatchStatus.UPCOMING,
            ),
        ]

    async def get_matches(
        self,
        status: Optional[MatchStatus] = None,
        tournament: Optional[str] = None,
    ) -> list[Match]:
        results = self._matches

        if status:
            results = [m for m in results if m.status == status]

        if tournament:
            results = [
                m for m in results
                if tournament.lower() in m.tournament.name.lower()
            ]

        return sorted(results, key=lambda m: m.date)

    async def get_match_by_id(self, match_id: str) -> Optional[Match]:
        """Buscar partido por ID."""
        for match in self._matches:
            if match.id == match_id:
                return match
        return None

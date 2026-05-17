import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from app.models.db_models import MatchDB
from app.repositories.matches_repository import MatchesRepository
from app.models.match import MatchStatus, Surface


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="function")
async def db_session():
    """Crea una base de datos real en memoria para cada test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_factory() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
async def repository(db_session):
    """Repositorio con sesión real."""
    return MatchesRepository(db_session)

@pytest.fixture
async def sample_match(db_session):
    """Inserta un partido de ejemplo en la BD real."""
    match = MatchDB(
        id="match_123",
        player_home_id="player_1",
        player_home_name="Novak Djokovic",
        player_home_country="Serbia",
        player_home_ranking=1,
        player_away_id="player_2",
        player_away_name="Carlos Alcaraz",
        player_away_country="Spain",
        player_away_ranking=2,
        tournament_id="tour_1",
        tournament_name="Wimbledon",
        tournament_surface="grass",
        tournament_category="Grand Slam",
        tournament_location="London",
        date=datetime.now(),
        status="upcoming",
        score=""
    )
    db_session.add(match)
    await db_session.commit()
    return match


class TestMatchesRepository:
    """Pruebas reales del repositorio (sin mocks)."""

    @pytest.mark.asyncio
    async def test_get_all_success(self, repository, sample_match):
        matches = await repository.get_all()
        assert len(matches) == 1
        assert matches[0].id == "match_123"
        assert matches[0].player_home.name == "Novak Djokovic"

    @pytest.mark.asyncio
    async def test_get_all_empty(self, repository):
        matches = await repository.get_all()
        assert len(matches) == 0

    @pytest.mark.asyncio
    async def test_get_all_with_status_filter(self, repository, sample_match):
        matches = await repository.get_all(status="upcoming")
        assert len(matches) == 1
        matches = await repository.get_all(status="finished")
        assert len(matches) == 0

    @pytest.mark.asyncio
    async def test_get_all_with_tournament_filter(self, repository, sample_match):
        matches = await repository.get_all(tournament="Wimbledon")
        assert len(matches) == 1
        matches = await repository.get_all(tournament="Roland")
        assert len(matches) == 0

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, repository, sample_match):
        match = await repository.get_by_id("match_123")
        assert match is not None
        assert match.player_home.name == "Novak Djokovic"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        match = await repository.get_by_id("nonexistent")
        assert match is None

    @pytest.mark.asyncio
    async def test_insert_many_success(self, repository, db_session):
        matches_data = [
            {
                "id": "new1",
                "player_home_id": "p1",
                "player_away_id": "p2",
                "tournament_id": "t1",
                "date": datetime.now(),
                "status": "upcoming"
            },
            {
                "id": "new2",
                "player_home_id": "p3",
                "player_away_id": "p4",
                "tournament_id": "t1",
                "date": datetime.now(),
                "status": "upcoming"
            }
        ]
        await repository.insert_many(matches_data)
        all_matches = await repository.get_all()
        assert len(all_matches) == 2

    @pytest.mark.asyncio
    async def test_insert_many_failure(self, repository):
        # Datos inválidos (falta campo obligatorio: player_home_id)
        matches_data = [{"id": "bad", "date": datetime.now()}]
        with pytest.raises(Exception):
            await repository.insert_many(matches_data)

    @pytest.mark.asyncio
    async def test_delete_all_success(self, repository, sample_match):
        await repository.delete_all()
        matches = await repository.get_all()
        assert len(matches) == 0

    @pytest.mark.asyncio
    async def test_delete_all_failure(self, repository):
        # No hay datos, delete_all debe funcionar igual
        await repository.delete_all()  # No debe lanzar error
        matches = await repository.get_all()
        assert len(matches) == 0

    def test_to_pydantic_with_minimal_data(self, repository):
        minimal_match = MatchDB(
            id="min_id",
            player_home_id="ph1",
            player_away_id="pa1",
            tournament_id="t1",
            date=datetime.now()
        )
        result = repository._to_pydantic(minimal_match)
        assert result.player_home.name == "Unknown"
        assert result.tournament.name == "Unknown Tournament"
        assert result.status == MatchStatus.UPCOMING

    def test_to_pydantic_with_full_data(self, repository, sample_match):
        # sample_match es un objeto MatchDB real
        result = repository._to_pydantic(sample_match)
        assert result.player_home.name == "Novak Djokovic"
        assert result.tournament.surface == Surface.GRASS
        assert result.status == MatchStatus.UPCOMING

    def test_to_pydantic_with_uppercase_values(self, repository):
        uppercase_match = MatchDB(
            id="up_id",
            player_home_id="ph1",
            player_home_name="Player",
            player_away_id="pa1",
            player_away_name="Opponent",
            tournament_id="t1",
            tournament_name="Tournament",
            tournament_surface="GRASS",
            date=datetime.now(),
            status="FINISHED"
        )
        result = repository._to_pydantic(uppercase_match)
        assert result.tournament.surface == Surface.GRASS
        assert result.status == MatchStatus.FINISHED

    @pytest.mark.asyncio
    async def test_get_all_ordering(self, repository, db_session):
        # Insertar partidos con diferentes fechas
        from datetime import timedelta
        base_date = datetime.now()
        for i, days in enumerate([-2, -1, 0]):
            match = MatchDB(
                id=f"order_{i}",
                player_home_id=f"p{i}",
                player_away_id=f"p{i+1}",
                tournament_id="t1",
                date=base_date + timedelta(days=days),
                status="upcoming"
            )
            db_session.add(match)
        await db_session.commit()
        
        matches = await repository.get_all()
        # Deberían venir ordenados por fecha ascendente
        dates = [m.date for m in matches]
        assert dates == sorted(dates)

    @pytest.mark.asyncio
    async def test_get_by_id_with_nonexistent_tournament_surface(self, repository, db_session):
        match = MatchDB(
            id="no_surface",
            player_home_id="ph1",
            player_away_id="pa1",
            tournament_id="t1",
            date=datetime.now(),
            tournament_surface=None
        )
        db_session.add(match)
        await db_session.commit()
        
        result = await repository.get_by_id("no_surface")
        assert result is not None
        assert result.tournament.surface == Surface.HARD

    @pytest.mark.asyncio
    async def test_get_all_with_case_insensitive_tournament_filter(self, repository, sample_match):
        matches = await repository.get_all(tournament="wimbledon")
        assert len(matches) == 1

    @pytest.mark.asyncio
    async def test_get_all_with_status_and_tournament_filters(self, repository, sample_match):
        matches = await repository.get_all(status="upcoming", tournament="Wimbledon")
        assert len(matches) == 1
        matches = await repository.get_all(status="finished", tournament="Wimbledon")
        assert len(matches) == 0

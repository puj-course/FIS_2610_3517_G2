"""
Tests para modelos SQLAlchemy, create_tables y save_combination_to_db.

Usa SQLite en memoria — no requiere PostgreSQL.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from app.core.database import Base

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    import app.models.db_models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session_factory(db_engine):
    return async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)


class TestDbModelsMetadata:

    def test_combinations_table_registered(self):
        import app.models.db_models  # noqa: F401
        assert "combinations" in Base.metadata.tables

    def test_selections_table_registered(self):
        import app.models.db_models  # noqa: F401
        assert "selections" in Base.metadata.tables

    def test_matches_table_registered(self):
        import app.models.db_models  # noqa: F401
        assert "matches" in Base.metadata.tables

    def test_player_stats_table_registered(self):
        import app.models.db_models  # noqa: F401
        assert "player_stats" in Base.metadata.tables

    def test_head_to_head_table_registered(self):
        import app.models.db_models  # noqa: F401
        assert "head_to_head" in Base.metadata.tables


class TestDbModelsDefaults:

    @pytest.mark.anyio
    async def test_combination_db_defaults_naive_datetime(self, session_factory):
        from app.models.db_models import CombinationDB

        async with session_factory() as session:
            async with session.begin():
                comb = CombinationDB(id="comb_test_001")
                session.add(comb)

            await session.refresh(comb)
            assert comb.created_at is not None
            assert comb.created_at.tzinfo is None
            assert comb.updated_at is not None
            assert comb.updated_at.tzinfo is None

    @pytest.mark.anyio
    async def test_selection_db_defaults_naive_datetime(self, session_factory):
        from app.models.db_models import CombinationDB, SelectionDB

        async with session_factory() as session:
            async with session.begin():
                comb = CombinationDB(id="comb_sel_test")
                session.add(comb)

            async with session.begin():
                sel = SelectionDB(
                    id="sel_test_001",
                    combination_id="comb_sel_test",
                    match_id="match_001",
                    player_home_name="Player A",
                    player_away_name="Player B",
                    tournament_name="Test Open",
                    match_date=datetime(2026, 6, 1, 10, 0),
                )
                session.add(sel)

            await session.refresh(sel)
            assert sel.added_at is not None
            assert sel.added_at.tzinfo is None

    def test_combination_db_has_onupdate(self):
        from app.models.db_models import CombinationDB
        col = CombinationDB.__table__.c.updated_at
        assert col.onupdate is not None

    def test_combination_created_at_default_callable(self):
        from app.models.db_models import CombinationDB
        col = CombinationDB.__table__.c.created_at
        result = col.default.arg(None)
        assert isinstance(result, datetime)
        assert result.tzinfo is None

    def test_combination_updated_at_default_callable(self):
        from app.models.db_models import CombinationDB
        col = CombinationDB.__table__.c.updated_at
        result = col.default.arg(None)
        assert isinstance(result, datetime)
        assert result.tzinfo is None

    def test_combination_updated_at_onupdate_callable(self):
        from app.models.db_models import CombinationDB
        col = CombinationDB.__table__.c.updated_at
        result = col.onupdate.arg(None)
        assert isinstance(result, datetime)
        assert result.tzinfo is None

    def test_selection_added_at_default_callable(self):
        from app.models.db_models import SelectionDB
        col = SelectionDB.__table__.c.added_at
        result = col.default.arg(None)
        assert isinstance(result, datetime)
        assert result.tzinfo is None


class TestCreateTables:

    @pytest.mark.anyio
    async def test_create_tables_registers_models(self):
        from app.core.database import create_tables
        with patch("app.core.database.engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_ctx = AsyncMock()
            mock_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_ctx.__aexit__ = AsyncMock(return_value=False)
            mock_engine.begin.return_value = mock_ctx

            await create_tables()

            mock_conn.run_sync.assert_called_once()
            assert "combinations" in Base.metadata.tables


class TestSaveCombinationToDb:

    @pytest.mark.anyio
    async def test_save_mock_mode_returns_saved_false(self):
        from app.services.combination_service import CombinationService

        service = CombinationService()
        comb = service.create_combination()

        with patch("app.core.config.get_settings") as mock_settings:
            mock_s = MagicMock()
            mock_s.data_mode = "mock"
            mock_settings.return_value = mock_s

            result = await service.save_combination_to_db(comb.id)

        assert result["saved"] is False
        assert result["combination_id"] == comb.id

    @pytest.mark.anyio
    async def test_save_database_mode_inserts_combination(self, session_factory):
        from app.services.combination_service import CombinationService
        from app.models.db_models import CombinationDB

        service = CombinationService()
        comb = service.create_combination()

        with patch("app.core.config.get_settings") as mock_settings, \
             patch("app.core.database.AsyncSessionLocal", session_factory):
            mock_s = MagicMock()
            mock_s.data_mode = "database"
            mock_settings.return_value = mock_s

            result = await service.save_combination_to_db(comb.id)

        assert result["saved"] is True
        assert result["combination_id"] == comb.id

        async with session_factory() as session:
            db_comb = await session.get(CombinationDB, comb.id)
            assert db_comb is not None
            assert db_comb.created_at.tzinfo is None

    @pytest.mark.anyio
    async def test_save_database_mode_with_selections(self, session_factory):
        from app.services.combination_service import CombinationService
        from app.models.db_models import SelectionDB
        from app.models.combination import Selection

        service = CombinationService()
        comb = service.create_combination()

        sel = Selection(
            match_id="match_001",
            player_home_name="Carlos Alcaraz",
            player_away_name="Novak Djokovic",
            tournament_name="Roland Garros",
            match_date=datetime(2026, 6, 1, 14, 0),
        )
        comb.selections.append(sel)

        with patch("app.core.config.get_settings") as mock_settings, \
             patch("app.core.database.AsyncSessionLocal", session_factory):
            mock_s = MagicMock()
            mock_s.data_mode = "database"
            mock_settings.return_value = mock_s

            result = await service.save_combination_to_db(comb.id)

        assert result["saved"] is True
        assert result["total_selections"] == 1

        async with session_factory() as session:
            rows = (await session.execute(
                select(SelectionDB).where(SelectionDB.combination_id == comb.id)
            )).scalars().all()
            assert len(rows) == 1
            assert rows[0].match_id == "match_001"
            assert rows[0].added_at.tzinfo is None

    @pytest.mark.anyio
    async def test_save_database_mode_upsert_updates_existing(self, session_factory):
        from app.services.combination_service import CombinationService
        from app.models.db_models import CombinationDB
        from app.models.combination import Selection

        service = CombinationService()
        comb = service.create_combination()

        with patch("app.core.config.get_settings") as mock_settings, \
             patch("app.core.database.AsyncSessionLocal", session_factory):
            mock_s = MagicMock()
            mock_s.data_mode = "database"
            mock_settings.return_value = mock_s

            await service.save_combination_to_db(comb.id)

            sel = Selection(
                match_id="match_002",
                player_home_name="Rafa Nadal",
                player_away_name="Roger Federer",
                tournament_name="Wimbledon",
                match_date=datetime(2026, 7, 1, 15, 0),
            )
            comb.selections.append(sel)

            result = await service.save_combination_to_db(comb.id)

        assert result["saved"] is True
        assert result["total_selections"] == 1

    @pytest.mark.anyio
    async def test_save_nonexistent_combination_raises(self):
        from app.services.combination_service import CombinationService
        from app.core.exceptions import NotFoundException

        service = CombinationService()

        with pytest.raises(NotFoundException):
            await service.save_combination_to_db("comb_nonexistent")

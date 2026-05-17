"""
Configuración global de pytest y fixtures.
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.database import Base
from app.repositories.matches_repository import MatchesRepository
from tests.factories import MatchFactory

# URL para SQLite en memoria
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session():
    """Crea una sesión real de BD en memoria para pruebas."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Crear todas las tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Crear fábrica de sesiones
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_factory() as session:
        yield session
    
    # Limpiar después de las pruebas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def repository(db_session):
    """Repositorio real con sesión real."""
    return MatchesRepository(db_session)


@pytest.fixture
def match_factory():
    """Fixture para acceder al factory."""
    return MatchFactory


@pytest.fixture
def sample_match(match_factory):
    """Fixture que devuelve un match de ejemplo válido."""
    return match_factory.create()


@pytest.fixture
def sample_matches_batch(match_factory):
    """Fixture que devuelve 3 matches válidos."""
    return match_factory.create_batch(3)

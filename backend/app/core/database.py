"""
Configuración de la conexión a PostgreSQL con SQLAlchemy async.

Uso:
    from app.core.database import get_db, create_tables

    # En endpoints como dependencia:
    async def my_endpoint(db: AsyncSession = Depends(get_db)):
        ...

    # Al iniciar la app:
    await create_tables()
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


Base = declarative_base()


async def get_db():
    """Dependencia de FastAPI — genera una sesión de BD por request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Crear todas las tablas definidas en los modelos."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """Eliminar todas las tablas (usar solo en tests)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

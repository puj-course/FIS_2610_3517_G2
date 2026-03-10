from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación OddsEngine."""

    app_name: str = "OddsEngine"
    debug: bool = True

    # API externa de tenis
    api_provider: str = "mock"
    api_sports_key: str = ""
    api_sports_base_url: str = "https://v1.tennis.api-sports.io"

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/oddsengine"
    database_sync_url: str = "postgresql://postgres:postgres@localhost:5432/oddsengine"

    # Modo de datos: "mock" usa datos en memoria, "database" usa PostgreSQL
    data_mode: str = "mock"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

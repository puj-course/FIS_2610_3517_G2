from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    data_mode: str = "mock"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/oddsengine"
    database_sync_url: str = "postgresql://postgres:postgres@localhost:5432/oddsengine"
    debug: bool = True

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""
Punto de entrada de la aplicación OddsEngine.

Configura FastAPI, CORS, logging, handlers de errores, rutas y base de datos.
El frontend React corre por separado con Vite (puerto 5173).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import matches
from app.routes import combinations
from app.routes import stats
from app.core.error_handlers import register_error_handlers
from app.core.logging_config import setup_logging
from app.core.config import get_settings

# Configurar logging al iniciar
setup_logging(log_level="INFO")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de inicio y cierre de la aplicación."""
    # Startup: crear tablas si se usa PostgreSQL
    if settings.data_mode == "database":
        from app.core.database import create_tables
        await create_tables()
    yield
    # Shutdown (cleanup si necesario)


app = FastAPI(
    title="OddsEngine API",
    description="Motor probabilístico para análisis de apuestas de tenis",
    version="0.5.0",
    lifespan=lifespan,
)

# CORS para permitir peticiones del frontend React (Vite en puerto 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar manejadores globales de excepciones
register_error_handlers(app)

# Registrar rutas API
app.include_router(matches.router, prefix="/api")
app.include_router(combinations.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.get("/health")
async def health_check():
    """Endpoint de salud para verificar que el servicio está corriendo."""
    return {
        "status": "ok",
        "service": "OddsEngine",
        "version": "0.5.0",
        "data_mode": settings.data_mode,
    }

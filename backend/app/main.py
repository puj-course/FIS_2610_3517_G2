
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.routes import matches, combinations, stats
from app.routes import probability, history
from app.core.error_handlers import register_error_handlers
from app.core.logging_config import setup_logging
from app.core.config import get_settings
from app.core.metrics import setup_metrics

setup_logging(log_level="INFO")
logger = logging.getLogger("oddsengine")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.data_mode == "database":
        from app.core.database import create_tables
        await create_tables()
        logger.info("Tablas PostgreSQL verificadas")
    logger.info(f"OddsEngine v1.0.0 iniciado — modo: {settings.data_mode}")
    yield
    logger.info("OddsEngine detenido")


app = FastAPI(
    title="OddsEngine API",
    description="Motor probabilístico para análisis de apuestas de tenis",
    version="1.0.0",
    lifespan=lifespan,
)

setup_metrics(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 1)
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response


register_error_handlers(app)

app.include_router(matches.router, prefix="/api")
app.include_router(combinations.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(probability.router, prefix="/api")
app.include_router(history.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "OddsEngine", "version": "1.0.0", "data_mode": settings.data_mode}


@app.get("/health/detailed")
async def health_detailed():
    db_status = "not_configured"
    if settings.data_mode == "database":
        try:
            from app.core.database import engine
            from sqlalchemy import text
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            db_status = "connected"
        except Exception:
            db_status = "disconnected"
    return {"status": "ok", "service": "OddsEngine", "version": "1.0.0", "data_mode": settings.data_mode, "database": db_status}



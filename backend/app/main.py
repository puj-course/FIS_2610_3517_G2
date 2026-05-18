
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.routes import matches, combinations, stats
from app.routes import probability, history, auth
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

    bot_app = None
    if settings.telegram_bot_token:
        try:
            from app.telegram import create_bot_application
            bot_app = create_bot_application(settings.telegram_bot_token)
            await bot_app.initialize()
            await bot_app.start()
            await bot_app.updater.start_polling()
            logger.info("Telegram Bot iniciado")
        except Exception:
            logger.exception("Error iniciando Telegram Bot")
            bot_app = None

    logger.info("OddsEngine v1.0.0 iniciado — modo: %s", settings.data_mode)
    yield

    if bot_app:
        try:
            await bot_app.updater.stop()
            await bot_app.stop()
            await bot_app.shutdown()
            logger.info("Telegram Bot detenido")
        except Exception:
            logger.exception("Error deteniendo Telegram Bot")

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
    logger.info("%s %s → %s (%sms)", request.method, request.url.path, response.status_code, duration)
    return response


register_error_handlers(app)

app.include_router(matches.router, prefix="/api")
app.include_router(combinations.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(probability.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(auth.router, prefix="/api")


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
        except SQLAlchemyError:
            db_status = "disconnected"
    return {"status": "ok", "service": "OddsEngine", "version": "1.0.0", "data_mode": settings.data_mode, "database": db_status}



"""
Tests unitarios para el lifespan de backend/app/main.py

Cubre los escenarios del bot de Telegram en el ciclo de vida:
- Sin TELEGRAM_BOT_TOKEN: el bot no inicia.
- Con TELEGRAM_BOT_TOKEN: el bot inicia y se detiene correctamente.
- Error al iniciar el bot: FastAPI sigue funcionando.
- Error al detener el bot: no rompe el shutdown.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.anyio
async def test_lifespan_without_token_does_not_start_bot():
    """Sin TELEGRAM_BOT_TOKEN, el bot no debe iniciar."""
    mock_settings = MagicMock()
    mock_settings.data_mode = "mock"
    mock_settings.telegram_bot_token = ""

    with patch("app.main.settings", mock_settings), \
         patch("app.telegram.create_bot_application") as mock_create:
        from app.main import lifespan, app

        async with lifespan(app):
            pass

        mock_create.assert_not_called()


@pytest.mark.anyio
async def test_lifespan_with_token_starts_and_stops_bot():
    """Con TELEGRAM_BOT_TOKEN, el bot debe iniciar y detenerse."""
    mock_settings = MagicMock()
    mock_settings.data_mode = "mock"
    mock_settings.telegram_bot_token = "fake-token-for-test"

    mock_bot_app = MagicMock()
    mock_bot_app.initialize = AsyncMock()
    mock_bot_app.start = AsyncMock()
    mock_bot_app.stop = AsyncMock()
    mock_bot_app.shutdown = AsyncMock()
    mock_bot_app.updater = MagicMock()
    mock_bot_app.updater.start_polling = AsyncMock()
    mock_bot_app.updater.stop = AsyncMock()

    with patch("app.main.settings", mock_settings), \
         patch("app.telegram.create_bot_application", return_value=mock_bot_app) as mock_create:
        from app.main import lifespan, app

        async with lifespan(app):
            mock_create.assert_called_once_with("fake-token-for-test")
            mock_bot_app.initialize.assert_awaited_once()
            mock_bot_app.start.assert_awaited_once()
            mock_bot_app.updater.start_polling.assert_awaited_once()

        # Verificar shutdown
        mock_bot_app.updater.stop.assert_awaited_once()
        mock_bot_app.stop.assert_awaited_once()
        mock_bot_app.shutdown.assert_awaited_once()


@pytest.mark.anyio
async def test_lifespan_bot_startup_error_does_not_crash():
    """Si el bot falla al iniciar, FastAPI sigue funcionando."""
    mock_settings = MagicMock()
    mock_settings.data_mode = "mock"
    mock_settings.telegram_bot_token = "fake-token-error"

    with patch("app.main.settings", mock_settings), \
         patch("app.telegram.create_bot_application", side_effect=RuntimeError("Token invalido")):
        from app.main import lifespan, app

        # No debe lanzar excepcion
        async with lifespan(app):
            pass


@pytest.mark.anyio
async def test_lifespan_bot_shutdown_error_does_not_crash():
    """Si el bot falla al detenerse, el shutdown no se rompe."""
    mock_settings = MagicMock()
    mock_settings.data_mode = "mock"
    mock_settings.telegram_bot_token = "fake-token-shutdown-error"

    mock_bot_app = MagicMock()
    mock_bot_app.initialize = AsyncMock()
    mock_bot_app.start = AsyncMock()
    mock_bot_app.stop = AsyncMock(side_effect=RuntimeError("Shutdown error"))
    mock_bot_app.shutdown = AsyncMock()
    mock_bot_app.updater = MagicMock()
    mock_bot_app.updater.start_polling = AsyncMock()
    mock_bot_app.updater.stop = AsyncMock()

    with patch("app.main.settings", mock_settings), \
         patch("app.telegram.create_bot_application", return_value=mock_bot_app):
        from app.main import lifespan, app

        # No debe lanzar excepcion
        async with lifespan(app):
            pass


@pytest.mark.anyio
async def test_lifespan_database_mode_creates_tables():
    """En modo database, debe llamar create_tables."""
    mock_settings = MagicMock()
    mock_settings.data_mode = "database"
    mock_settings.telegram_bot_token = ""

    mock_create_tables = AsyncMock()

    with patch("app.main.settings", mock_settings), \
         patch("app.core.database.create_tables", mock_create_tables):
        from app.main import lifespan, app

        async with lifespan(app):
            mock_create_tables.assert_awaited_once()


@pytest.mark.anyio
async def test_lifespan_mock_mode_skips_tables():
    """En modo mock, no debe llamar create_tables."""
    mock_settings = MagicMock()
    mock_settings.data_mode = "mock"
    mock_settings.telegram_bot_token = ""

    with patch("app.main.settings", mock_settings), \
         patch("app.core.database.create_tables", new_callable=AsyncMock) as mock_ct:
        from app.main import lifespan, app

        async with lifespan(app):
            mock_ct.assert_not_awaited()

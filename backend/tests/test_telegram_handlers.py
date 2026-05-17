import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_update_and_context(args=None):
    update = MagicMock()
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.args = args or []
    return update, context


@pytest.mark.anyio
async def test_start_handler_sends_welcome():
    from app.telegram.handlers import start_handler

    update, context = _make_update_and_context()
    await start_handler(update, context)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "OddsEngine" in text
    assert "/matches" in text


@pytest.mark.anyio
async def test_help_handler_sends_commands():
    from app.telegram.handlers import help_handler

    update, context = _make_update_and_context()
    await help_handler(update, context)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "/health" in text
    assert "/match" in text


@pytest.mark.anyio
async def test_health_handler_returns_status():
    from app.telegram.handlers import health_handler

    update, context = _make_update_and_context()
    await health_handler(update, context)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "ok" in text
    assert "1.0.0" in text


@pytest.mark.anyio
async def test_matches_handler_returns_list():
    from app.telegram.handlers import matches_handler

    update, context = _make_update_and_context()
    await matches_handler(update, context)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Partidos de tenis" in text or "No se encontraron" in text


@pytest.mark.anyio
async def test_matches_handler_with_status_filter():
    from app.telegram.handlers import matches_handler

    update, context = _make_update_and_context(args=["upcoming"])
    await matches_handler(update, context)

    update.message.reply_text.assert_called_once()


@pytest.mark.anyio
async def test_matches_handler_invalid_status():
    from app.telegram.handlers import matches_handler

    update, context = _make_update_and_context(args=["invalid_status"])
    await matches_handler(update, context)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "Error" in text


@pytest.mark.anyio
async def test_match_handler_no_args_shows_usage():
    from app.telegram.handlers import match_handler

    update, context = _make_update_and_context(args=[])
    await match_handler(update, context)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "match_id" in text


@pytest.mark.anyio
async def test_match_handler_not_found():
    from app.telegram.handlers import match_handler

    update, context = _make_update_and_context(args=["nonexistent_999"])
    await match_handler(update, context)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "no encontrado" in text


@pytest.mark.anyio
async def test_match_handler_found():
    from app.telegram.handlers import match_handler

    update, context = _make_update_and_context(args=["match_001"])
    await match_handler(update, context)

    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "match_001" in text

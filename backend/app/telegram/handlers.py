import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.services.match_service import get_match_service
from app.core.config import get_settings
from app.telegram.formatters import (
    format_match_summary,
    format_match_detail,
    format_match_list,
    format_health,
)

logger = logging.getLogger("oddsengine")

WELCOME_TEXT = (
    "<b>Bienvenido a OddsEngine Bot!</b>\n"
    "Analizador de probabilidades de tenis.\n\n"
    "<b>Comandos disponibles:</b>\n"
    "/matches — Listar partidos de tenis\n"
    "/matches &lt;status&gt; — Filtrar por estado (upcoming, live, finished)\n"
    "/match &lt;id&gt; — Ver detalle de un partido\n"
    "/health — Estado del servicio\n"
    "/help — Mostrar esta ayuda"
)

MAX_MATCHES_DISPLAY = 10


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, parse_mode="HTML")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, parse_mode="HTML")


async def health_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = get_settings()
    text = format_health(status="ok", version="1.0.0", data_mode=settings.data_mode)
    await update.message.reply_text(text, parse_mode="HTML")


async def matches_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_filter = context.args[0] if context.args else None
    service = get_match_service()

    try:
        matches = await service.get_matches(status=status_filter)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    total = len(matches)
    display = matches[:MAX_MATCHES_DISPLAY]
    text = format_match_list(display, total)
    await update.message.reply_text(text, parse_mode="HTML")


async def match_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Uso: /match &lt;match_id&gt;\nEjemplo: /match match_001",
            parse_mode="HTML",
        )
        return

    match_id = context.args[0]
    service = get_match_service()

    try:
        match = await service.get_match_by_id(match_id)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    if match is None:
        await update.message.reply_text(f"Partido '{match_id}' no encontrado.")
        return

    text = format_match_detail(match)
    await update.message.reply_text(text, parse_mode="HTML")

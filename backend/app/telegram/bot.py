from telegram.ext import ApplicationBuilder, CommandHandler

from app.telegram.handlers import (
    start_handler,
    help_handler,
    health_handler,
    matches_handler,
    match_handler,
)


def create_bot_application(token: str):
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("health", health_handler))
    application.add_handler(CommandHandler("matches", matches_handler))
    application.add_handler(CommandHandler("match", match_handler))
    return application

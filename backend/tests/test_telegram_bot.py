"""
Tests unitarios para backend/app/telegram/bot.py

Verifica que create_bot_application() registra correctamente
los 5 command handlers sin hacer llamadas reales a Telegram.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestCreateBotApplication:
    """Tests para la factory create_bot_application."""

    @patch("app.telegram.bot.CommandHandler")
    @patch("app.telegram.bot.ApplicationBuilder")
    def test_creates_application_with_token(self, mock_builder_cls, mock_cmd_handler):
        from app.telegram.bot import create_bot_application

        mock_app = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_builder_cls.return_value = mock_builder

        result = create_bot_application("fake-token-123")

        mock_builder.token.assert_called_once_with("fake-token-123")
        mock_builder.build.assert_called_once()
        assert result is mock_app

    @patch("app.telegram.bot.CommandHandler")
    @patch("app.telegram.bot.ApplicationBuilder")
    def test_registers_start_handler(self, mock_builder_cls, mock_cmd_handler):
        from app.telegram.bot import create_bot_application
        from app.telegram.handlers import start_handler

        mock_app = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_builder_cls.return_value = mock_builder

        create_bot_application("fake-token")

        calls = mock_cmd_handler.call_args_list
        command_names = [call[0][0] for call in calls]
        assert "start" in command_names

    @patch("app.telegram.bot.CommandHandler")
    @patch("app.telegram.bot.ApplicationBuilder")
    def test_registers_help_handler(self, mock_builder_cls, mock_cmd_handler):
        from app.telegram.bot import create_bot_application
        from app.telegram.handlers import help_handler

        mock_app = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_builder_cls.return_value = mock_builder

        create_bot_application("fake-token")

        calls = mock_cmd_handler.call_args_list
        command_names = [call[0][0] for call in calls]
        assert "help" in command_names

    @patch("app.telegram.bot.CommandHandler")
    @patch("app.telegram.bot.ApplicationBuilder")
    def test_registers_health_handler(self, mock_builder_cls, mock_cmd_handler):
        from app.telegram.bot import create_bot_application
        from app.telegram.handlers import health_handler

        mock_app = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_builder_cls.return_value = mock_builder

        create_bot_application("fake-token")

        calls = mock_cmd_handler.call_args_list
        command_names = [call[0][0] for call in calls]
        assert "health" in command_names

    @patch("app.telegram.bot.CommandHandler")
    @patch("app.telegram.bot.ApplicationBuilder")
    def test_registers_matches_handler(self, mock_builder_cls, mock_cmd_handler):
        from app.telegram.bot import create_bot_application
        from app.telegram.handlers import matches_handler

        mock_app = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_builder_cls.return_value = mock_builder

        create_bot_application("fake-token")

        calls = mock_cmd_handler.call_args_list
        command_names = [call[0][0] for call in calls]
        assert "matches" in command_names

    @patch("app.telegram.bot.CommandHandler")
    @patch("app.telegram.bot.ApplicationBuilder")
    def test_registers_match_handler(self, mock_builder_cls, mock_cmd_handler):
        from app.telegram.bot import create_bot_application
        from app.telegram.handlers import match_handler

        mock_app = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_builder_cls.return_value = mock_builder

        create_bot_application("fake-token")

        calls = mock_cmd_handler.call_args_list
        command_names = [call[0][0] for call in calls]
        assert "match" in command_names

    @patch("app.telegram.bot.CommandHandler")
    @patch("app.telegram.bot.ApplicationBuilder")
    def test_registers_exactly_five_handlers(self, mock_builder_cls, mock_cmd_handler):
        from app.telegram.bot import create_bot_application

        mock_app = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_builder_cls.return_value = mock_builder

        create_bot_application("fake-token")

        assert mock_app.add_handler.call_count == 5

    @patch("app.telegram.bot.CommandHandler")
    @patch("app.telegram.bot.ApplicationBuilder")
    def test_all_five_commands_registered(self, mock_builder_cls, mock_cmd_handler):
        from app.telegram.bot import create_bot_application

        mock_app = MagicMock()
        mock_builder = MagicMock()
        mock_builder.token.return_value = mock_builder
        mock_builder.build.return_value = mock_app
        mock_builder_cls.return_value = mock_builder

        create_bot_application("fake-token")

        calls = mock_cmd_handler.call_args_list
        command_names = {call[0][0] for call in calls}
        expected = {"start", "help", "health", "matches", "match"}
        assert command_names == expected

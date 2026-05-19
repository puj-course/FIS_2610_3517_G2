"""Tests para el servicio de notificaciones Telegram."""

import logging
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

import httpx

from app.services.telegram_notification_service import TelegramNotificationService


def _make_service(enabled=True, token="fake-token", chat_id="12345", threshold=30.0, http_client=None):
    return TelegramNotificationService(
        enabled=enabled,
        token=token,
        chat_id=chat_id,
        threshold=threshold,
        http_client=http_client,
    )


class TestTelegramDisabled:

    @pytest.mark.anyio
    async def test_send_disabled_returns_false(self):
        service = _make_service(enabled=False)
        result = await service.send_combination_saved(
            combination_id="comb_001",
            total_selections=3,
            total_probability=45.0,
            risk_level="medium",
        )
        assert result is False

    @pytest.mark.anyio
    async def test_send_disabled_logs_debug(self, caplog):
        service = _make_service(enabled=False)
        with caplog.at_level(logging.DEBUG, logger="oddsengine"):
            await service.send_combination_saved(
                combination_id="comb_001",
                total_selections=3,
                total_probability=45.0,
                risk_level="medium",
            )
        assert "deshabilitado" in caplog.text

    @pytest.mark.anyio
    async def test_send_disabled_does_not_call_http(self):
        mock_client = AsyncMock()
        service = _make_service(enabled=False, http_client=mock_client)
        await service.send_combination_saved(
            combination_id="comb_001",
            total_selections=2,
            total_probability=60.0,
            risk_level="low",
        )
        mock_client.post.assert_not_called()


class TestMissingConfig:

    @pytest.mark.anyio
    async def test_missing_token_returns_false(self):
        service = _make_service(token="")
        result = await service.send_combination_saved(
            combination_id="comb_001",
            total_selections=2,
            total_probability=50.0,
            risk_level="medium",
        )
        assert result is False

    @pytest.mark.anyio
    async def test_missing_token_logs_warning(self, caplog):
        service = _make_service(token="")
        with caplog.at_level(logging.WARNING, logger="oddsengine"):
            await service.send_combination_saved(
                combination_id="comb_001",
                total_selections=2,
                total_probability=50.0,
                risk_level="medium",
            )
        assert "falta TELEGRAM_BOT_TOKEN" in caplog.text

    @pytest.mark.anyio
    async def test_missing_chat_id_returns_false(self):
        service = _make_service(chat_id="")
        result = await service.send_combination_saved(
            combination_id="comb_001",
            total_selections=2,
            total_probability=50.0,
            risk_level="medium",
        )
        assert result is False

    @pytest.mark.anyio
    async def test_missing_chat_id_logs_warning(self, caplog):
        service = _make_service(chat_id="")
        with caplog.at_level(logging.WARNING, logger="oddsengine"):
            await service.send_combination_saved(
                combination_id="comb_001",
                total_selections=2,
                total_probability=50.0,
                risk_level="medium",
            )
        assert "falta TELEGRAM_CHAT_ID" in caplog.text


class TestSendSuccess:

    @pytest.mark.anyio
    async def test_send_success_returns_true(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        service = _make_service(http_client=mock_client)
        result = await service.send_combination_saved(
            combination_id="comb_abc",
            total_selections=3,
            total_probability=55.0,
            risk_level="low",
        )
        assert result is True

    @pytest.mark.anyio
    async def test_send_calls_telegram_api(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        service = _make_service(http_client=mock_client)
        await service.send_combination_saved(
            combination_id="comb_abc",
            total_selections=2,
            total_probability=40.0,
            risk_level="medium",
        )

        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        url = call_args[0][0]
        assert "api.telegram.org" in url
        assert "sendMessage" in url

    @pytest.mark.anyio
    async def test_send_includes_chat_id_in_payload(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        service = _make_service(chat_id="99999", http_client=mock_client)
        await service.send_combination_saved(
            combination_id="comb_abc",
            total_selections=2,
            total_probability=40.0,
            risk_level="medium",
        )

        payload = mock_client.post.call_args[1]["json"]
        assert payload["chat_id"] == "99999"


class TestSendErrors:

    @pytest.mark.anyio
    async def test_http_error_returns_false(self):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        service = _make_service(http_client=mock_client)
        result = await service.send_combination_saved(
            combination_id="comb_001",
            total_selections=2,
            total_probability=50.0,
            risk_level="medium",
        )
        assert result is False

    @pytest.mark.anyio
    async def test_timeout_returns_false(self):
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.TimeoutException("timeout")

        service = _make_service(http_client=mock_client)
        result = await service.send_combination_saved(
            combination_id="comb_001",
            total_selections=2,
            total_probability=50.0,
            risk_level="medium",
        )
        assert result is False

    @pytest.mark.anyio
    async def test_generic_exception_returns_false(self):
        mock_client = AsyncMock()
        mock_client.post.side_effect = RuntimeError("network down")

        service = _make_service(http_client=mock_client)
        result = await service.send_combination_saved(
            combination_id="comb_001",
            total_selections=2,
            total_probability=50.0,
            risk_level="medium",
        )
        assert result is False


class TestMessageFormatting:

    @pytest.mark.anyio
    async def test_low_risk_no_alert(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        service = _make_service(http_client=mock_client, threshold=30.0)
        await service.send_combination_saved(
            combination_id="comb_low",
            total_selections=2,
            total_probability=55.0,
            risk_level="low",
        )

        payload = mock_client.post.call_args[1]["json"]
        text = payload["text"]
        assert "comb_low" in text
        assert "55.0%" in text
        assert "⚠️ Alerta" not in text

    @pytest.mark.anyio
    async def test_high_risk_includes_alert(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        service = _make_service(http_client=mock_client, threshold=30.0)
        await service.send_combination_saved(
            combination_id="comb_high",
            total_selections=4,
            total_probability=8.5,
            risk_level="high",
        )

        payload = mock_client.post.call_args[1]["json"]
        text = payload["text"]
        assert "⚠️ Alerta" in text
        assert "8.5%" in text

    @pytest.mark.anyio
    async def test_medium_risk_below_threshold_includes_alert(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        service = _make_service(http_client=mock_client, threshold=30.0)
        await service.send_combination_saved(
            combination_id="comb_med",
            total_selections=3,
            total_probability=25.0,
            risk_level="medium",
        )

        payload = mock_client.post.call_args[1]["json"]
        text = payload["text"]
        assert "⚠️ Alerta" in text

    @pytest.mark.anyio
    async def test_medium_risk_above_threshold_no_alert(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        service = _make_service(http_client=mock_client, threshold=30.0)
        await service.send_combination_saved(
            combination_id="comb_ok",
            total_selections=2,
            total_probability=45.0,
            risk_level="medium",
        )

        payload = mock_client.post.call_args[1]["json"]
        text = payload["text"]
        assert "⚠️ Alerta" not in text


class TestTokenNotInLogs:

    @pytest.mark.anyio
    async def test_token_not_logged_on_success(self, caplog):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        service = _make_service(token="super-secret-token-xyz", http_client=mock_client)
        with caplog.at_level(logging.DEBUG, logger="oddsengine"):
            await service.send_combination_saved(
                combination_id="comb_001",
                total_selections=2,
                total_probability=50.0,
                risk_level="medium",
            )
        assert "super-secret-token-xyz" not in caplog.text

    @pytest.mark.anyio
    async def test_token_not_logged_on_error(self, caplog):
        mock_client = AsyncMock()
        mock_client.post.side_effect = RuntimeError("fail")

        service = _make_service(token="secret-tok-999", http_client=mock_client)
        with caplog.at_level(logging.DEBUG, logger="oddsengine"):
            await service.send_combination_saved(
                combination_id="comb_001",
                total_selections=2,
                total_probability=50.0,
                risk_level="medium",
            )
        assert "secret-tok-999" not in caplog.text


class TestIntegrationWithSave:

    @pytest.mark.anyio
    async def test_notification_failure_does_not_break_save(self, client):
        """El guardado de combinada funciona aunque Telegram falle."""
        resp = await client.post("/api/combinations")
        comb_id = resp.json()["id"]
        await client.post(
            f"/api/combinations/{comb_id}/matches",
            json={"match_id": "match_001"},
        )
        await client.post(
            f"/api/combinations/{comb_id}/matches",
            json={"match_id": "match_002"},
        )

        with patch(
            "app.routes.combinations.get_telegram_notification_service"
        ) as mock_get, patch(
            "app.core.config.get_settings"
        ) as mock_settings:
            mock_s = MagicMock()
            mock_s.data_mode = "mock"
            mock_settings.return_value = mock_s

            mock_notifier = AsyncMock()
            mock_notifier.send_combination_saved.side_effect = RuntimeError("Telegram down")
            mock_get.return_value = mock_notifier

            resp = await client.post(f"/api/combinations/{comb_id}/save")

        assert resp.status_code == 200
        data = resp.json()
        assert data["combination_id"] == comb_id

    @pytest.mark.anyio
    async def test_save_calls_notification_service(self, client):
        """Verificar que el endpoint de guardar intenta notificar."""
        resp = await client.post("/api/combinations")
        comb_id = resp.json()["id"]
        await client.post(
            f"/api/combinations/{comb_id}/matches",
            json={"match_id": "match_001"},
        )
        await client.post(
            f"/api/combinations/{comb_id}/matches",
            json={"match_id": "match_002"},
        )

        with patch(
            "app.routes.combinations.get_telegram_notification_service"
        ) as mock_get, patch(
            "app.core.config.get_settings"
        ) as mock_settings:
            mock_s = MagicMock()
            mock_s.data_mode = "mock"
            mock_settings.return_value = mock_s

            mock_notifier = AsyncMock()
            mock_notifier.send_combination_saved.return_value = True
            mock_get.return_value = mock_notifier

            await client.post(f"/api/combinations/{comb_id}/save")

        mock_notifier.send_combination_saved.assert_called_once()
        call_kwargs = mock_notifier.send_combination_saved.call_args[1]
        assert call_kwargs["combination_id"] == comb_id
        assert call_kwargs["total_selections"] == 2

    @pytest.mark.anyio
    async def test_save_mock_mode_still_notifies(self, client):
        """En DATA_MODE=mock (saved=false), la notificación se dispara igual."""
        resp = await client.post("/api/combinations")
        comb_id = resp.json()["id"]
        await client.post(
            f"/api/combinations/{comb_id}/matches",
            json={"match_id": "match_001"},
        )
        await client.post(
            f"/api/combinations/{comb_id}/matches",
            json={"match_id": "match_002"},
        )

        with patch(
            "app.routes.combinations.get_telegram_notification_service"
        ) as mock_get, patch(
            "app.core.config.get_settings"
        ) as mock_settings:
            mock_s = MagicMock()
            mock_s.data_mode = "mock"
            mock_settings.return_value = mock_s

            mock_notifier = AsyncMock()
            mock_notifier.send_combination_saved.return_value = True
            mock_get.return_value = mock_notifier

            resp = await client.post(f"/api/combinations/{comb_id}/save")

        assert resp.status_code == 200
        data = resp.json()
        assert data["saved"] is False
        mock_notifier.send_combination_saved.assert_called_once()

    @pytest.mark.anyio
    async def test_save_logs_when_notification_not_sent(self, client, caplog):
        """Si la notificación retorna False, se loggea info descriptivo."""
        resp = await client.post("/api/combinations")
        comb_id = resp.json()["id"]
        await client.post(
            f"/api/combinations/{comb_id}/matches",
            json={"match_id": "match_001"},
        )
        await client.post(
            f"/api/combinations/{comb_id}/matches",
            json={"match_id": "match_002"},
        )

        with patch(
            "app.routes.combinations.get_telegram_notification_service"
        ) as mock_get, patch(
            "app.core.config.get_settings"
        ) as mock_settings:
            mock_s = MagicMock()
            mock_s.data_mode = "mock"
            mock_settings.return_value = mock_s

            mock_notifier = AsyncMock()
            mock_notifier.send_combination_saved.return_value = False
            mock_get.return_value = mock_notifier

            with caplog.at_level(logging.INFO, logger="oddsengine"):
                await client.post(f"/api/combinations/{comb_id}/save")

        assert "no enviada" in caplog.text

    @pytest.mark.anyio
    async def test_save_logs_exception_detail(self, client, caplog):
        """Si la notificación lanza excepción, el log incluye el motivo."""
        resp = await client.post("/api/combinations")
        comb_id = resp.json()["id"]
        await client.post(
            f"/api/combinations/{comb_id}/matches",
            json={"match_id": "match_001"},
        )
        await client.post(
            f"/api/combinations/{comb_id}/matches",
            json={"match_id": "match_002"},
        )

        with patch(
            "app.routes.combinations.get_telegram_notification_service"
        ) as mock_get, patch(
            "app.core.config.get_settings"
        ) as mock_settings:
            mock_s = MagicMock()
            mock_s.data_mode = "mock"
            mock_settings.return_value = mock_s

            mock_notifier = AsyncMock()
            mock_notifier.send_combination_saved.side_effect = RuntimeError("connection refused")
            mock_get.return_value = mock_notifier

            with caplog.at_level(logging.WARNING, logger="oddsengine"):
                resp = await client.post(f"/api/combinations/{comb_id}/save")

        assert resp.status_code == 200
        assert "connection refused" in caplog.text

"""Servicio de notificaciones por Telegram para combinadas guardadas."""

import logging
from typing import Optional

import httpx

from app.core.config import get_settings

logger = logging.getLogger("oddsengine")

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramNotificationService:

    def __init__(
        self,
        enabled: Optional[bool] = None,
        token: Optional[str] = None,
        chat_id: Optional[str] = None,
        threshold: Optional[float] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        settings = get_settings()
        self._enabled = enabled if enabled is not None else settings.telegram_enabled
        self._token = token if token is not None else settings.telegram_bot_token
        self._chat_id = chat_id if chat_id is not None else settings.telegram_chat_id
        self._threshold = (
            threshold if threshold is not None
            else settings.telegram_low_probability_threshold
        )
        self._http_client = http_client

    def _is_configured(self) -> bool:
        if not self._enabled:
            logger.debug("Telegram deshabilitado (TELEGRAM_ENABLED=false)")
            return False
        if not self._token:
            logger.warning("Telegram habilitado pero falta TELEGRAM_BOT_TOKEN")
            return False
        if not self._chat_id:
            logger.warning("Telegram habilitado pero falta TELEGRAM_CHAT_ID")
            return False
        return True

    def _format_message(
        self,
        combination_id: str,
        total_selections: int,
        total_probability: float,
        risk_level: str,
    ) -> str:
        lines = [
            "✅ OddsEngine — Combinada guardada",
            f"ID: {combination_id}",
            f"Selecciones: {total_selections}",
            f"Probabilidad estimada: {total_probability}%",
            f"Riesgo: {risk_level.upper()}",
        ]

        if self._is_high_risk(total_probability, risk_level):
            lines.append("")
            lines.append(
                "⚠️ Alerta: la probabilidad de éxito es baja. "
                "Revisa tu selección antes de apostar."
            )

        return "\n".join(lines)

    def _is_high_risk(self, total_probability: float, risk_level: str) -> bool:
        return (
            risk_level.upper() == "HIGH"
            or total_probability < self._threshold
        )

    async def send_combination_saved(
        self,
        combination_id: str,
        total_selections: int,
        total_probability: float,
        risk_level: str,
    ) -> bool:
        if not self._is_configured():
            return False

        text = self._format_message(
            combination_id, total_selections, total_probability, risk_level
        )
        return await self._send_message(text)

    async def _send_message(self, text: str) -> bool:
        url = TELEGRAM_API_URL.format(token=self._token)
        payload = {"chat_id": self._chat_id, "text": text, "parse_mode": "HTML"}

        try:
            if self._http_client:
                response = self._http_client
                resp = await response.post(url, json=payload, timeout=10)
            else:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url, json=payload, timeout=10)

            if resp.status_code == 200:
                logger.info("Notificación Telegram enviada correctamente")
                return True

            logger.warning(
                "Telegram respondió con status %s", resp.status_code
            )
            return False

        except httpx.TimeoutException:
            logger.warning("Timeout enviando notificación Telegram")
            return False
        except Exception:
            logger.warning("Error enviando notificación Telegram")
            return False


_notification_service: Optional[TelegramNotificationService] = None


def get_telegram_notification_service() -> TelegramNotificationService:
    global _notification_service
    if _notification_service is None:
        _notification_service = TelegramNotificationService()
    return _notification_service


def reset_telegram_notification_service() -> None:
    global _notification_service
    _notification_service = None

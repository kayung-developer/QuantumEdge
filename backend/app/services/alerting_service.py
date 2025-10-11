"""
AuraQuant - Alerting Dispatch Service
"""
import httpx
import logging
from enum import Enum
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertingService:
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=10.0)

    async def _send_slack_message(self, message: str, level: AlertLevel):
        """Sends a formatted message to a Slack webhook."""
        if not settings.ALERTING_SLACK_WEBHOOK_URL:
            return

        color_map = {
            AlertLevel.INFO: "#3B82F6",  # Blue
            AlertLevel.WARNING: "#FBBF24",  # Amber
            AlertLevel.CRITICAL: "#EF4444",  # Red
        }

        payload = {
            "attachments": [
                {
                    "color": color_map.get(level, "#8B949E"),
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*[{level.upper()}]* - AuraQuant Platform\n{message}"
                            }
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        try:
            await self.http_client.post(settings.ALERTING_SLACK_WEBHOOK_URL, json=payload)
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    async def _send_telegram_message(self, message: str, level: AlertLevel):
        """Sends a message to a Telegram chat via the bot API."""
        if not settings.ALERTING_TELEGRAM_BOT_TOKEN or not settings.ALERTING_TELEGRAM_CHAT_ID:
            return

        url = f"https://api.telegram.org/bot{settings.ALERTING_TELEGRAM_BOT_TOKEN}/sendMessage"

        level_icon = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.CRITICAL: "🔥",
        }

        # Telegram uses a simple MarkdownV2 format
        formatted_message = (
            f"*{level_icon.get(level)} [{level.upper()}] - AuraQuant Platform*\n\n"
            f"{message}"
        )

        payload = {
            'chat_id': settings.ALERTING_TELEGRAM_CHAT_ID,
            'text': formatted_message,
            'parse_mode': 'MarkdownV2'
        }

        try:
            await self.http_client.post(url, json=payload)
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")

    async def dispatch(
            self,
            message: str,
            level: AlertLevel = AlertLevel.INFO,
            to_slack: bool = True,
            to_telegram: bool = True
    ):
        """
        Dispatches an alert to all configured channels.
        This is the main method to be called by other services.
        """
        logger.info(f"Dispatching alert (level: {level}): {message}")
        tasks = []
        if to_slack:
            tasks.append(self._send_slack_message(message, level))
        if to_telegram:
            tasks.append(self._send_telegram_message(message, level))

        if tasks:
            await asyncio.gather(*tasks)


# Create a single instance
alerting_service = AlertingService()
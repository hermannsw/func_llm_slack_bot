"""Slack webhook client implementation."""

import logging
from typing import Dict, Any

import requests

from ..domain.exceptions import SlackWebhookError
from ..domain.services import MessageSender
from .config import Config

logger = logging.getLogger(__name__)


class SlackWebhookSender(MessageSender):
    """Implementation of message sender using Slack webhooks."""
    
    def __init__(self, config: Config) -> None:
        """Initialize Slack webhook sender.
        
        Args:
            config: Application configuration
        """
        self._config = config
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "SlackBot/1.0"
        })
    
    def send_message(self, message: str, channel: str = "") -> bool:
        """Send message to Slack via webhook.
        
        Args:
            message: The message content to send
            channel: The target channel (unused in webhook implementation)
            
        Returns:
            True if message was sent successfully
            
        Raises:
            SlackWebhookError: If message sending fails
        """
        try:
            payload = {"text": message}
            
            logger.info(
                "Sending Slack message",
                extra={"message_length": len(message)}
            )
            
            response = self._session.post(
                self._config.SLACK_WEBHOOK_URL,
                json=payload,
                timeout=self._config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            logger.info("Slack message sent successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error("Slack webhook request failed", extra={"error": str(e)})
            raise SlackWebhookError(f"Failed to send Slack message: {e}") from e
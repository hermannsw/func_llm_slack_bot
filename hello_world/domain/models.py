"""Domain models for the Slack bot application."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class SlackMessage:
    """Represents a Slack message."""
    text: str
    user_id: str
    channel_id: str
    timestamp: float


@dataclass(frozen=True)
class SlackEvent:
    """Represents a Slack event."""
    event_type: str
    event_data: Dict[str, Any]
    challenge: Optional[str] = None


@dataclass(frozen=True)
class LLMRequest:
    """Represents a request to the LLM service."""
    application_id: int
    message: str
    stream: bool = False


@dataclass(frozen=True)
class LLMResponse:
    """Represents a response from the LLM service."""
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class APIResponse:
    """Represents an API Gateway response."""
    status_code: int
    body: str
    headers: Optional[Dict[str, str]] = None
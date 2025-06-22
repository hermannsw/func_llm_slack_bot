"""Slack event parsing implementation."""

import json
import logging
from typing import Dict, Any

from ..domain.exceptions import InvalidEventError, SlackEventError
from ..domain.models import SlackEvent
from ..domain.services import EventParser

logger = logging.getLogger(__name__)


class SlackEventParser(EventParser):
    """Implementation of event parser for Slack events."""
    
    def parse_slack_event(self, raw_event: Dict[str, Any]) -> SlackEvent:
        """Parse raw event data into SlackEvent domain model.
        
        Args:
            raw_event: Raw event data from API Gateway
            
        Returns:
            Parsed SlackEvent domain model
            
        Raises:
            InvalidEventError: If event format is invalid
        """
        try:
            body_str = raw_event.get("body", "{}")
            if not body_str:
                raise InvalidEventError("Event body is empty")
            
            body = json.loads(body_str)
            
            # Handle URL verification challenge
            if body.get("type") == "url_verification":
                return SlackEvent(
                    event_type="url_verification",
                    event_data=body,
                    challenge=body.get("challenge")
                )
            
            # Handle event callback
            if body.get("type") == "event_callback":
                event_data = body.get("event", {})
                event_type = event_data.get("type", "unknown")
                
                return SlackEvent(
                    event_type=event_type,
                    event_data=body
                )
            
            # Unknown event type
            return SlackEvent(
                event_type="unknown",
                event_data=body
            )
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse event JSON", extra={"error": str(e)})
            raise InvalidEventError(f"Invalid JSON in event body: {e}") from e
        except Exception as e:
            logger.error("Unexpected error parsing event", extra={"error": str(e)})
            raise InvalidEventError(f"Failed to parse event: {e}") from e
    
    def extract_message_text(self, event: SlackEvent) -> str:
        """Extract message text from Slack event.
        
        Args:
            event: Parsed Slack event
            
        Returns:
            Extracted message text
            
        Raises:
            SlackEventError: If message text cannot be extracted
        """
        try:
            if event.event_type != "app_mention":
                raise SlackEventError(f"Cannot extract message from event type: {event.event_type}")
            
            # Navigate the nested structure to extract message text
            event_data = event.event_data.get("event", {})
            blocks = event_data.get("blocks", [])
            
            if not blocks:
                raise SlackEventError("No blocks found in app mention event")
            
            # Extract text from the first block's elements
            first_block = blocks[0]
            elements = first_block.get("elements", [])
            
            if not elements:
                raise SlackEventError("No elements found in first block")
            
            first_element = elements[0]
            sub_elements = first_element.get("elements", [])
            
            if len(sub_elements) < 2:
                raise SlackEventError("Insufficient elements to extract message text")
            
            # The message text is typically in the second sub-element
            message_text = sub_elements[1].get("text", "").strip()
            
            if not message_text:
                raise SlackEventError("Message text is empty")
            
            logger.info(
                "Message text extracted successfully",
                extra={"text_length": len(message_text)}
            )
            
            return message_text
            
        except (KeyError, IndexError, TypeError) as e:
            logger.error("Failed to extract message text", extra={"error": str(e)})
            raise SlackEventError(f"Cannot extract message text: {e}") from e
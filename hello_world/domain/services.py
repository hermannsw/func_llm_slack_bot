"""Service protocols for dependency injection."""

from typing import Protocol

from .models import LLMRequest, LLMResponse, SlackEvent


class LLMService(Protocol):
    """Protocol for LLM service implementations."""
    
    def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response from LLM service.
        
        Args:
            request: The LLM request containing message and metadata
            
        Returns:
            LLM response with generated content
            
        Raises:
            LLMServiceError: If the LLM service request fails
        """
        ...


class MessageSender(Protocol):
    """Protocol for message sending implementations."""
    
    def send_message(self, message: str, channel: str) -> bool:
        """Send message to specified channel.
        
        Args:
            message: The message content to send
            channel: The target channel identifier
            
        Returns:
            True if message was sent successfully, False otherwise
            
        Raises:
            SlackWebhookError: If message sending fails
        """
        ...


class EventParser(Protocol):
    """Protocol for event parsing implementations."""
    
    def parse_slack_event(self, raw_event: dict) -> SlackEvent:
        """Parse raw event data into SlackEvent domain model.
        
        Args:
            raw_event: Raw event data from API Gateway
            
        Returns:
            Parsed SlackEvent domain model
            
        Raises:
            InvalidEventError: If event format is invalid
        """
        ...
    
    def extract_message_text(self, event: SlackEvent) -> str:
        """Extract message text from Slack event.
        
        Args:
            event: Parsed Slack event
            
        Returns:
            Extracted message text
            
        Raises:
            SlackEventError: If message text cannot be extracted
        """
        ...
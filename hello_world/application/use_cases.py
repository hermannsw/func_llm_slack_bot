"""Application use cases for the Slack bot."""

import logging
from typing import Dict, Any

from ..domain.exceptions import SlackBotError
from ..domain.models import APIResponse, LLMRequest, SlackEvent
from ..domain.services import LLMService, MessageSender, EventParser

logger = logging.getLogger(__name__)


class HelloWorldUseCase:
    """Use case for hello world functionality."""
    
    def execute(self) -> APIResponse:
        """Execute hello world use case.
        
        Returns:
            API response with hello world message
        """
        logger.info("Executing hello world use case")
        
        return APIResponse(
            status_code=200,
            body='{"message": "hello world"}'
        )


class SlackEventUseCase:
    """Use case for processing Slack events."""
    
    def __init__(
        self,
        event_parser: EventParser,
        llm_service: LLMService,
        message_sender: MessageSender,
        application_id: int
    ) -> None:
        """Initialize Slack event use case.
        
        Args:
            event_parser: Event parser implementation
            llm_service: LLM service implementation
            message_sender: Message sender implementation
            application_id: LLM application ID
        """
        self._event_parser = event_parser
        self._llm_service = llm_service
        self._message_sender = message_sender
        self._application_id = application_id
    
    def execute(self, raw_event: Dict[str, Any]) -> APIResponse:
        """Execute Slack event processing use case.
        
        Args:
            raw_event: Raw event data from API Gateway
            
        Returns:
            API response based on event type
        """
        try:
            logger.info("Processing Slack event")
            
            # Parse the event
            slack_event = self._event_parser.parse_slack_event(raw_event)
            
            # Handle different event types
            if slack_event.event_type == "url_verification":
                return self._handle_url_verification(slack_event)
            elif slack_event.event_type == "app_mention":
                return self._handle_app_mention(slack_event)
            else:
                logger.warning(f"Unhandled event type: {slack_event.event_type}")
                return APIResponse(
                    status_code=400,
                    body='{"error": "Unrecognized event type"}'
                )
        
        except SlackBotError as e:
            logger.error(f"Slack bot error: {e}")
            return APIResponse(
                status_code=400,
                body=f'{{"error": "{str(e)}"}}'
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return APIResponse(
                status_code=500,
                body=f'{{"error": "Internal server error"}}'
            )
    
    def _handle_url_verification(self, event: SlackEvent) -> APIResponse:
        """Handle URL verification challenge.
        
        Args:
            event: Parsed Slack event
            
        Returns:
            API response with challenge string
        """
        logger.info("Handling URL verification")
        
        challenge = event.challenge or ""
        return APIResponse(
            status_code=200,
            body=challenge
        )
    
    def _handle_app_mention(self, event: SlackEvent) -> APIResponse:
        """Handle app mention event.
        
        Args:
            event: Parsed Slack event
            
        Returns:
            API response with processing result
        """
        try:
            logger.info("Handling app mention")
            
            # Extract message text
            message_text = self._event_parser.extract_message_text(event)
            
            # Create LLM request
            llm_request = LLMRequest(
                application_id=self._application_id,
                message=message_text,
                stream=False
            )
            
            # Get LLM response
            llm_response = self._llm_service.generate_response(llm_request)
            
            # Send response to Slack
            self._message_sender.send_message(llm_response.content)
            
            logger.info("App mention processed successfully")
            
            return APIResponse(
                status_code=200,
                body='{"message": "App mention processed"}'
            )
            
        except SlackBotError as e:
            logger.error(f"Error processing app mention: {e}")
            return APIResponse(
                status_code=500,
                body=f'{{"error": "{str(e)}"}}'
            )
        except Exception as e:
            logger.error(f"Unexpected error processing app mention: {e}")
            return APIResponse(
                status_code=500,
                body=f'{{"error": "Internal server error"}}'
            )
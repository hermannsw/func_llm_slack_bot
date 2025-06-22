"""Lambda handlers for the Slack bot application."""

import json
import logging
from typing import Any, Dict

from ..application.use_cases import HelloWorldUseCase, SlackEventUseCase
from ..domain.exceptions import ConfigurationError
from ..infrastructure.config import Config
from ..infrastructure.event_parser import SlackEventParser
from ..infrastructure.llm_client import LLMApiClient
from ..infrastructure.slack_client import SlackWebhookSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "extra": %(extra)s}',
)
logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for hello world endpoint.
    
    Args:
        event: API Gateway Lambda Proxy Input Format
        context: Lambda Context runtime methods and attributes
        
    Returns:
        API Gateway Lambda Proxy Output Format
    """
    try:
        logger.info("Hello world lambda invoked", extra={})
        
        use_case = HelloWorldUseCase()
        response = use_case.execute()
        
        return {
            "statusCode": response.status_code,
            "body": response.body,
            "headers": response.headers or {}
        }
        
    except Exception as e:
        logger.error("Hello world lambda failed", extra={"error": str(e)})
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }


def challenge_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for Slack challenge endpoint.
    
    Args:
        event: API Gateway Lambda Proxy Input Format
        context: Lambda Context runtime methods and attributes
        
    Returns:
        API Gateway Lambda Proxy Output Format
    """
    try:
        logger.info("Challenge lambda invoked", extra={})
        
        # Initialize dependencies
        config = Config()
        event_parser = SlackEventParser()
        llm_service = LLMApiClient(config)
        message_sender = SlackWebhookSender(config)
        
        # Execute use case
        use_case = SlackEventUseCase(
            event_parser=event_parser,
            llm_service=llm_service,
            message_sender=message_sender,
            application_id=config.LLM_APPLICATION_ID
        )
        
        response = use_case.execute(event)
        
        return {
            "statusCode": response.status_code,
            "body": response.body,
            "headers": response.headers or {}
        }
        
    except ConfigurationError as e:
        logger.error("Configuration error", extra={"error": str(e)})
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Configuration error"})
        }
    except Exception as e:
        logger.error("Challenge lambda failed", extra={"error": str(e)})
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
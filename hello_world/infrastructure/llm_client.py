"""LLM service client implementation."""

import json
import logging
from typing import Dict, Any

import requests

from ..domain.exceptions import LLMServiceError
from ..domain.models import LLMRequest, LLMResponse
from ..domain.services import LLMService
from .config import Config

logger = logging.getLogger(__name__)


class LLMApiClient(LLMService):
    """Implementation of LLM service using HTTP API."""
    
    def __init__(self, config: Config) -> None:
        """Initialize LLM API client.
        
        Args:
            config: Application configuration
        """
        self._config = config
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "SlackBot/1.0"
        })
    
    def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response from LLM service.
        
        Args:
            request: The LLM request containing message and metadata
            
        Returns:
            LLM response with generated content
            
        Raises:
            LLMServiceError: If the LLM service request fails
        """
        try:
            payload = self._build_request_payload(request)
            
            logger.info(
                "Sending LLM request",
                extra={
                    "application_id": request.application_id,
                    "message_length": len(request.message)
                }
            )
            
            response = self._session.post(
                self._config.LLM_API_URL,
                json=payload,
                timeout=self._config.REQUEST_TIMEOUT,
                headers={"Authorization": ""}  # Empty as specified in original code
            )
            response.raise_for_status()
            
            response_data = response.json()
            content = self._extract_response_content(response_data)
            
            logger.info("LLM request successful", extra={"content_length": len(content)})
            
            return LLMResponse(content=content, metadata=response_data)
            
        except requests.exceptions.RequestException as e:
            logger.error("LLM API request failed", extra={"error": str(e)})
            raise LLMServiceError(f"LLM API request failed: {e}") from e
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            logger.error("LLM API response parsing failed", extra={"error": str(e)})
            raise LLMServiceError(f"Invalid LLM API response: {e}") from e
    
    def _build_request_payload(self, request: LLMRequest) -> Dict[str, Any]:
        """Build request payload for LLM API.
        
        Args:
            request: LLM request object
            
        Returns:
            Request payload dictionary
        """
        return {
            "application_id": request.application_id,
            "stream": request.stream,
            "messages": [
                {
                    "role": "user",
                    "contents": [
                        {
                            "type": "text",
                            "content": request.message
                        }
                    ]
                }
            ]
        }
    
    def _extract_response_content(self, response_data: Dict[str, Any]) -> str:
        """Extract content from LLM API response.
        
        Args:
            response_data: Raw response data from LLM API
            
        Returns:
            Extracted content string
            
        Raises:
            KeyError: If response format is unexpected
        """
        return response_data["reply"][0]["contents"][0]["content"]
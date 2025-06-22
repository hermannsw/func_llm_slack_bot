"""Refactored Lambda handlers using clean architecture.

This module provides backward compatibility while delegating to the new
clean architecture implementation.
"""

from typing import Any, Dict

from .presentation.handlers import lambda_handler as new_lambda_handler
from .presentation.handlers import challenge_handler as new_challenge_handler


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for hello world endpoint.
    
    Args:
        event: API Gateway Lambda Proxy Input Format
        context: Lambda Context runtime methods and attributes
        
    Returns:
        API Gateway Lambda Proxy Output Format
    """
    return new_lambda_handler(event, context)


def challenge_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for Slack challenge endpoint.
    
    Args:
        event: API Gateway Lambda Proxy Input Format
        context: Lambda Context runtime methods and attributes
        
    Returns:
        API Gateway Lambda Proxy Output Format
    """
    return new_challenge_handler(event, context)

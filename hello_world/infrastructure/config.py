"""Configuration management for the application."""

import os
from typing import Optional

from ..domain.exceptions import ConfigurationError


class Config:
    """Application configuration."""
    
    LLM_API_URL: str
    SLACK_WEBHOOK_URL: str
    LLM_APPLICATION_ID: int
    REQUEST_TIMEOUT: int
    
    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        self.LLM_API_URL = self._get_required_env("LLM_API_URL")
        self.SLACK_WEBHOOK_URL = self._get_required_env("SLACK_WEBHOOK_URL")
        self.LLM_APPLICATION_ID = int(self._get_optional_env("LLM_APPLICATION_ID", "3550"))
        self.REQUEST_TIMEOUT = int(self._get_optional_env("REQUEST_TIMEOUT", "30"))
    
    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error.
        
        Args:
            key: Environment variable name
            
        Returns:
            Environment variable value
            
        Raises:
            ConfigurationError: If required environment variable is not set
        """
        value = os.getenv(key)
        if not value:
            raise ConfigurationError(f"Required environment variable {key} not set")
        return value
    
    def _get_optional_env(self, key: str, default: str = "") -> str:
        """Get optional environment variable with default.
        
        Args:
            key: Environment variable name
            default: Default value if not set
            
        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)
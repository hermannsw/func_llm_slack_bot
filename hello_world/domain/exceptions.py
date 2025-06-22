"""Custom exceptions for the Slack bot application."""


class SlackBotError(Exception):
    """Base exception for Slack bot errors."""
    pass


class SlackEventError(SlackBotError):
    """Exception raised when Slack event processing fails."""
    pass


class LLMServiceError(SlackBotError):
    """Exception raised when LLM service fails."""
    pass


class SlackWebhookError(SlackBotError):
    """Exception raised when Slack webhook fails."""
    pass


class InvalidEventError(SlackBotError):
    """Exception raised when event format is invalid."""
    pass


class ConfigurationError(SlackBotError):
    """Exception raised when configuration is invalid."""
    pass
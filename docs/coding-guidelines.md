# Python Coding Guidelines

## Table of Contents
- [Overview](#overview)
- [Code Style](#code-style)
- [Clean Architecture Principles](#clean-architecture-principles)
- [Project Structure](#project-structure)
- [Naming Conventions](#naming-conventions)
- [Function and Class Design](#function-and-class-design)
- [Type Hints](#type-hints)
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Documentation](#documentation)
- [Dependencies](#dependencies)
- [Logging](#logging)
- [Performance](#performance)
- [Security](#security)

## Overview

This document outlines coding standards and best practices for Python development in this project. These guidelines emphasize modern Python practices, clean architecture principles, and maintainable code.

## Code Style

### PEP 8 Compliance
- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Use 4 spaces for indentation (no tabs)
- Line length: 88 characters (Black formatter default)
- Use trailing commas in multi-line structures

### Formatting Tools
- **Black**: Automatic code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .
```

### Import Organization
```python
# Standard library imports
import json
import os
from typing import Dict, List, Optional

# Third-party imports
import requests
from pydantic import BaseModel

# Local imports
from .models import SlackEvent
from .services import LLMService
```

## Clean Architecture Principles

### Dependency Inversion
- High-level modules should not depend on low-level modules
- Both should depend on abstractions
- Use interfaces/protocols for external dependencies

```python
from abc import ABC, abstractmethod
from typing import Protocol

class LLMService(Protocol):
    def generate_response(self, prompt: str) -> str: ...

class SlackBot:
    def __init__(self, llm_service: LLMService):
        self._llm_service = llm_service
```

### Separation of Concerns
- Each module should have a single responsibility
- Separate business logic from infrastructure concerns
- Use dependency injection for external services

### Layered Architecture
```
┌─────────────────────────────────────┐
│           Presentation Layer        │
│        (Lambda Handlers)            │
├─────────────────────────────────────┤
│          Application Layer          │
│        (Use Cases/Services)         │
├─────────────────────────────────────┤
│            Domain Layer             │
│        (Business Logic)             │
├─────────────────────────────────────┤
│         Infrastructure Layer        │
│     (External APIs, Databases)     │
└─────────────────────────────────────┘
```

## Project Structure

```
src/
├── domain/
│   ├── models/          # Domain entities
│   ├── repositories/    # Repository interfaces
│   └── services/        # Domain services
├── application/
│   ├── use_cases/       # Application use cases
│   └── services/        # Application services
├── infrastructure/
│   ├── api/            # External API clients
│   ├── repositories/   # Repository implementations
│   └── config/         # Configuration
└── presentation/
    ├── handlers/       # Lambda handlers
    └── serializers/    # Request/response serializers
```

## Naming Conventions

### Variables and Functions
- Use `snake_case` for variables and functions
- Use descriptive names that explain intent
- Avoid abbreviations unless widely understood

```python
# Good
user_message = event.get_message_text()
api_response = llm_service.generate_response(user_message)

# Bad
msg = event.get_msg()
resp = llm.gen(msg)
```

### Classes
- Use `PascalCase` for class names
- Use noun phrases that describe the entity

```python
class SlackEventHandler:
    pass

class LLMApiClient:
    pass
```

### Constants
- Use `UPPER_SNAKE_CASE` for constants
- Group related constants in classes or modules

```python
class APIConfig:
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    BASE_URL = "https://api.example.com"
```

## Function and Class Design

### Single Responsibility Principle
Each function should do one thing well:

```python
# Good
def extract_message_text(event: SlackEvent) -> str:
    """Extract message text from Slack event."""
    return event.blocks[0].elements[0].elements[1].text

def send_llm_request(message: str) -> str:
    """Send message to LLM API and return response."""
    # Implementation here
    pass

# Bad
def process_slack_event(event: SlackEvent) -> dict:
    """Process Slack event and return response."""
    # Extracts message, calls LLM, sends webhook - too many responsibilities
    pass
```

### Pure Functions
Prefer pure functions when possible:

```python
def format_slack_message(text: str, user_id: str) -> dict:
    """Format text into Slack message format."""
    return {
        "text": text,
        "user": user_id,
        "timestamp": time.time()
    }
```

### Immutability
Use immutable data structures when possible:

```python
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class SlackMessage:
    text: str
    user_id: str
    channel_id: str
    timestamp: float
```

## Type Hints

### Always Use Type Hints
- Use type hints for all function parameters and return values
- Use `typing` module for complex types
- Use `Optional` for nullable values

```python
from typing import Dict, List, Optional, Union

def process_slack_event(
    event: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Union[str, int]]:
    """Process Slack event and return response."""
    pass
```

### Use Protocols for Interfaces
```python
from typing import Protocol

class MessageSender(Protocol):
    def send_message(self, message: str, channel: str) -> bool: ...

class SlackWebhookSender:
    def send_message(self, message: str, channel: str) -> bool:
        # Implementation
        pass
```

## Error Handling

### Use Specific Exceptions
```python
class SlackBotError(Exception):
    """Base exception for Slack bot errors."""
    pass

class LLMServiceError(SlackBotError):
    """Exception raised when LLM service fails."""
    pass

class SlackWebhookError(SlackBotError):
    """Exception raised when Slack webhook fails."""
    pass
```

### Fail Fast Principle
```python
def process_app_mention(event: Dict[str, Any]) -> Dict[str, Any]:
    if not event:
        raise ValueError("Event cannot be empty")
    
    if event.get("type") != "event_callback":
        raise ValueError(f"Unexpected event type: {event.get('type')}")
    
    # Process event
    pass
```

### Context Managers for Resources
```python
from contextlib import contextmanager
from typing import Generator

@contextmanager
def api_client(base_url: str) -> Generator[requests.Session, None, None]:
    session = requests.Session()
    session.headers.update({"User-Agent": "SlackBot/1.0"})
    try:
        yield session
    finally:
        session.close()
```

## Testing

### Test Structure
```python
import pytest
from unittest.mock import Mock, patch

class TestSlackEventHandler:
    def test_handle_app_mention_success(self):
        # Arrange
        handler = SlackEventHandler(llm_service=Mock())
        event = {"type": "app_mention", "text": "Hello bot"}
        
        # Act
        result = handler.handle_event(event)
        
        # Assert
        assert result["statusCode"] == 200
    
    def test_handle_app_mention_invalid_event(self):
        # Arrange
        handler = SlackEventHandler(llm_service=Mock())
        
        # Act & Assert
        with pytest.raises(ValueError):
            handler.handle_event({})
```

### Use Fixtures
```python
@pytest.fixture
def mock_llm_service():
    service = Mock()
    service.generate_response.return_value = "Test response"
    return service

@pytest.fixture
def sample_slack_event():
    return {
        "type": "event_callback",
        "event": {
            "type": "app_mention",
            "text": "Hello <@U123> can you help?"
        }
    }
```

### Test Categories
- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test interactions between components
- **End-to-End Tests**: Test complete workflows

## Documentation

### Docstrings
Use Google-style docstrings:

```python
def send_llm_request(message: str, application_id: int) -> str:
    """Send message to LLM API and return response.
    
    Args:
        message: The user message to send to the LLM
        application_id: The application ID for the LLM service
        
    Returns:
        The LLM response text
        
    Raises:
        LLMServiceError: If the LLM API request fails
        ValueError: If message is empty or application_id is invalid
    """
    pass
```

### README Files
- Include setup instructions
- Document environment variables
- Provide usage examples
- Document deployment process

## Dependencies

### Dependency Management
- Use `pyproject.toml` for dependency specification
- Pin specific versions for production dependencies
- Use dependency groups for different environments

```toml
[project]
dependencies = [
    "requests>=2.32.0,<3.0.0",
    "pydantic>=2.0.0,<3.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]
```

### Minimize Dependencies
- Only add dependencies that provide significant value
- Prefer standard library solutions when possible
- Regularly audit and update dependencies

## Logging

### Structured Logging
```python
import logging
import json

logger = logging.getLogger(__name__)

def log_event(event_type: str, **kwargs):
    """Log structured event data."""
    log_data = {
        "event_type": event_type,
        "timestamp": time.time(),
        **kwargs
    }
    logger.info(json.dumps(log_data))

# Usage
log_event("app_mention_received", user_id="U123", channel="C456")
```

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General information about program execution
- **WARNING**: Something unexpected happened
- **ERROR**: Serious problem that prevented function execution
- **CRITICAL**: Very serious error that may cause program termination

## Performance

### Async/Await for I/O
```python
import asyncio
import aiohttp

async def fetch_llm_response(message: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.llm.example.com/chat",
            json={"message": message}
        ) as response:
            data = await response.json()
            return data["response"]
```

### Use Generators for Large Data
```python
def process_messages_batch(messages: List[str]) -> Generator[str, None, None]:
    """Process messages in batches to avoid memory issues."""
    for message in messages:
        yield process_single_message(message)
```

## Security

### Input Validation
```python
from pydantic import BaseModel, validator

class SlackEventInput(BaseModel):
    event_type: str
    user_id: str
    message: str
    
    @validator('message')
    def validate_message(cls, v):
        if len(v) > 1000:
            raise ValueError('Message too long')
        return v.strip()
```

### Environment Variables
```python
import os
from typing import Optional

def get_required_env(key: str) -> str:
    """Get required environment variable or raise error."""
    value = os.getenv(key)
    if not value:
        raise ValueError(f"Required environment variable {key} not set")
    return value

def get_optional_env(key: str, default: str = "") -> str:
    """Get optional environment variable with default."""
    return os.getenv(key, default)
```

### Secrets Management
- Never commit secrets to version control
- Use AWS Secrets Manager or Parameter Store for sensitive data
- Rotate secrets regularly

## Code Review Checklist

- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have type hints
- [ ] Functions have single responsibility
- [ ] Appropriate error handling is implemented
- [ ] Tests are written for new functionality
- [ ] Documentation is updated
- [ ] No hardcoded secrets or sensitive data
- [ ] Performance considerations are addressed
- [ ] Security best practices are followed

## Tools and Automation

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
```

### GitHub Actions
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install -e .[dev]
      - run: black --check .
      - run: isort --check-only .
      - run: flake8 .
      - run: mypy .
      - run: pytest
```

---

Remember: These guidelines are living documents that should evolve with the project and team needs. Regular reviews and updates ensure they remain relevant and useful.
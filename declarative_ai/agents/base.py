"""Base agent API wrapper with retry and structured output enforcement.

This is the single call point for all Claude API interactions. All agents
(Planner, Worker, State Generator, Validator) must call call_agent() from
this module — never call the SDK directly.

Centralizes:
- Rate limit retry with exponential backoff (tenacity)
- Parse-retry loop for structured output validation failures
- Structured output enforcement via client.beta.messages.parse()
"""
import os
from typing import TypeVar, Type

import anthropic
from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

T = TypeVar("T", bound=BaseModel)

# Lazy client — created only on first call to get_client()
_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    """Return the shared Anthropic client, creating it lazily on first call.

    Reads ANTHROPIC_API_KEY from os.environ. The client is NOT created at
    module import time to allow load_dotenv() to run before instantiation.
    """
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((anthropic.RateLimitError, anthropic.APIStatusError)),
)
def _call_api_with_retry(
    client: anthropic.Anthropic,
    model: str,
    system: str,
    user_message: str,
    response_model: Type[T],
) -> T:
    """Single API call — tenacity handles rate-limit and API status retries.

    Uses client.beta.messages.parse() for structured output enforcement.
    This is the beta structured outputs endpoint; the beta header is handled
    automatically by the SDK. Wrapped here as the single change point for
    when the feature exits beta.
    """
    message = client.beta.messages.parse(
        model=model,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user_message}],
        response_format=response_model,
    )
    return message.parsed


def call_agent(
    client: anthropic.Anthropic,
    system: str,
    user_message: str,
    response_model: Type[T],
    model: str = "claude-opus-4-5",
    max_parse_retries: int = 3,
) -> T:
    """Call Claude with structured output enforcement.

    Retries up to max_parse_retries on parse/validation failures, appending
    error context to the user prompt on each retry. Raises RuntimeError after
    exhausting retries.

    Rate limit errors (429) are retried transparently by tenacity inside
    _call_api_with_retry — up to 5 attempts with exponential backoff.

    Args:
        client: Anthropic client instance (use get_client() for the default).
        system: System prompt string.
        user_message: User prompt string.
        response_model: Pydantic model class for structured output enforcement.
        model: Claude model ID to use.
        max_parse_retries: Number of parse-retry attempts before raising.

    Returns:
        Validated Pydantic instance of response_model.

    Raises:
        RuntimeError: After max_parse_retries failed parse attempts.
    """
    last_error: Exception | None = None
    current_user_message = user_message

    for attempt in range(max_parse_retries):
        try:
            return _call_api_with_retry(
                client, model, system, current_user_message, response_model
            )
        except (ValidationError, ValueError) as exc:
            last_error = exc
            current_user_message = (
                f"{current_user_message}\n\n"
                f"[Retry {attempt + 1}/{max_parse_retries}] "
                f"Previous response failed validation: {exc}. "
                f"Respond ONLY with valid JSON matching the required schema."
            )

    raise RuntimeError(
        f"Agent call failed after {max_parse_retries} parse retries. "
        f"Last error: {last_error}"
    )

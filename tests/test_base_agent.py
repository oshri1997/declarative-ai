"""Tests for the base agent API wrapper with retry and schema enforcement.

These tests are RED until Plan 03 implements declarative_ai/agents/base.py.
"""
import pytest
from pydantic import BaseModel


class _SampleOutput(BaseModel):
    answer: str
    confidence: float


def test_call_agent_success(mocker, sample_spec_dict):
    """call_agent returns a Pydantic instance when the API responds correctly."""
    from declarative_ai.agents.base import call_agent

    mock_parse_response = mocker.MagicMock()
    mock_parse_response.parsed = _SampleOutput(answer="hello", confidence=0.99)

    mock_client = mocker.MagicMock()
    mock_client.beta.messages.parse.return_value = mock_parse_response

    result = call_agent(
        client=mock_client,
        system="You are a test assistant.",
        user_message="Say hello.",
        response_model=_SampleOutput,
    )
    assert isinstance(result, _SampleOutput)
    assert result.answer == "hello"


def test_parse_retry_exhaustion(mocker, sample_spec_dict):
    """call_agent raises RuntimeError after 3 failed parse attempts."""
    from pydantic import ValidationError
    from declarative_ai.agents.base import call_agent

    mock_client = mocker.MagicMock()

    class _BadModel(BaseModel):
        required_field: str

    # Create a real ValidationError for _BadModel with missing field
    try:
        _BadModel()
    except ValidationError as ve:
        real_ve = ve

    mock_client.beta.messages.parse.side_effect = real_ve

    with pytest.raises(RuntimeError):
        call_agent(
            client=mock_client,
            system="You are a test assistant.",
            user_message="Fail always.",
            response_model=_SampleOutput,
        )

    # Should have been called exactly 3 times before giving up
    assert mock_client.beta.messages.parse.call_count == 3


def test_rate_limit_retry(mocker):
    """call_agent retries transparently when RateLimitError is raised first time."""
    from anthropic import RateLimitError
    from declarative_ai.agents.base import call_agent

    success_response = mocker.MagicMock()
    success_response.parsed = _SampleOutput(answer="retried", confidence=0.5)

    mock_client = mocker.MagicMock()
    mock_client.beta.messages.parse.side_effect = [
        RateLimitError(
            message="rate limited",
            response=mocker.MagicMock(status_code=429, headers={}),
            body={},
        ),
        success_response,
    ]

    result = call_agent(
        client=mock_client,
        system="You are a test assistant.",
        user_message="Retry me.",
        response_model=_SampleOutput,
    )
    assert isinstance(result, _SampleOutput)
    assert result.answer == "retried"


def test_get_client_lazy_init(mocker):
    """Client is created lazily — not at module import time."""
    from declarative_ai.agents.base import get_client

    # Patch Anthropic constructor so we can detect when it's called
    mock_anthropic_cls = mocker.patch("declarative_ai.agents.base.anthropic.Anthropic")
    mock_anthropic_cls.return_value = mocker.MagicMock()

    # Importing base already happened — constructor should NOT have been called yet
    # (lazy init: client is created only when get_client() is first called)
    mock_anthropic_cls.assert_not_called()

    client = get_client()
    assert client is not None
    mock_anthropic_cls.assert_called_once()

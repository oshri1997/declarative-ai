"""Shared fixtures for all test files."""
from pathlib import Path

import pytest
import yaml


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_spec_dict():
    """Load tests/fixtures/simple_spec.yaml and return as a dict."""
    spec_path = FIXTURES_DIR / "simple_spec.yaml"
    with open(spec_path) as f:
        return yaml.safe_load(f)


@pytest.fixture
def sample_spec_path():
    """Return the Path to tests/fixtures/simple_spec.yaml."""
    return FIXTURES_DIR / "simple_spec.yaml"


@pytest.fixture
def fresh_build_state(sample_spec_dict):
    """Return a BuildState(spec=sample_spec_dict).

    NOTE: This fixture will fail with ImportError until Plan 03 implements state.py.
    That is expected RED behavior.
    """
    from declarative_ai.state import BuildState

    return BuildState(spec=sample_spec_dict)


@pytest.fixture
def mock_anthropic_client(mocker):
    """Mock anthropic.Anthropic client for testing agent calls."""
    return mocker.patch("anthropic.Anthropic")

"""Tests for SpecModel — the Pydantic schema for declarative YAML specs.

These tests are RED until Plan 02 implements declarative_ai/schema/spec_schema.py.
"""
import pytest
import yaml
from pathlib import Path


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_simple_spec() -> dict:
    with open(FIXTURES_DIR / "simple_spec.yaml") as f:
        return yaml.safe_load(f)


def test_load_valid_spec(sample_spec_dict):
    """SPEC-01: A valid spec dict is accepted and fields are accessible."""
    from declarative_ai.schema.spec_schema import SpecModel

    spec = SpecModel(**sample_spec_dict)
    assert spec.name == "todo-api"


def test_endpoints_field(sample_spec_dict):
    """SPEC-02: endpoints is a list; first entry has correct method."""
    from declarative_ai.schema.spec_schema import SpecModel

    spec = SpecModel(**sample_spec_dict)
    assert len(spec.endpoints) == 1
    assert spec.endpoints[0].method == "GET"


def test_components_field(sample_spec_dict):
    """SPEC-03: components is a list; first entry has correct name."""
    from declarative_ai.schema.spec_schema import SpecModel

    spec = SpecModel(**sample_spec_dict)
    assert len(spec.components) == 1
    assert spec.components[0].name == "TaskList"


def test_models_field(sample_spec_dict):
    """SPEC-04: models list; first model has 3 fields."""
    from declarative_ai.schema.spec_schema import SpecModel

    spec = SpecModel(**sample_spec_dict)
    assert len(spec.models) == 1
    task_model = spec.models[0]
    assert task_model.name == "Task"
    assert len(task_model.fields) == 3


def test_config_field(sample_spec_dict):
    """SPEC-05: config.env_vars and config.feature_flags are accessible."""
    from declarative_ai.schema.spec_schema import SpecModel

    spec = SpecModel(**sample_spec_dict)
    assert "DATABASE_URL" in spec.config.env_vars
    assert "enable_auth" in spec.config.feature_flags


def test_language_agnostic():
    """SPEC-06: SpecModel accepts any language and framework without error."""
    from declarative_ai.schema.spec_schema import SpecModel

    data = {
        "name": "my-api",
        "language": "rust",
        "framework": "actix",
    }
    spec = SpecModel(**data)
    assert spec.language == "rust"
    assert spec.framework == "actix"


def test_empty_spec_raises():
    """Pitfall 5: empty/None input must raise ValueError (not silently succeed)."""
    from declarative_ai.schema.spec_schema import SpecModel

    with pytest.raises((ValueError, TypeError)):
        SpecModel()


def test_minimal_spec():
    """SpecModel with only required name field; all optional fields default correctly."""
    from declarative_ai.schema.spec_schema import SpecModel

    spec = SpecModel(name="minimal-api")
    assert spec.name == "minimal-api"
    assert spec.endpoints == [] or spec.endpoints is None
    assert spec.components == [] or spec.components is None
    assert spec.models == [] or spec.models is None

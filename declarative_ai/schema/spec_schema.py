"""Pydantic models for the declarative AI spec schema.

SpecModel is the input contract for the entire system. Every agent reads the
spec through this schema. Validation errors surface at load time, not deep in
agent calls.

All language/framework/type fields are plain str — no Literal or enum
constraints — per SPEC-06 (language-agnostic design).
"""
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class EndpointSpec(BaseModel):
    """Describes a single API endpoint. SPEC-02."""

    method: str                           # "GET", "POST", etc. — plain string, no enum
    path: str                             # "/api/users"
    request_schema: dict[str, Any] = {}   # free-form shape description
    response_schema: dict[str, Any] = {}  # free-form shape description
    description: str = ""


class ComponentSpec(BaseModel):
    """Describes a UI component. SPEC-03."""

    name: str
    props: dict[str, Any] = {}  # prop name → type hint string
    behavior: str = ""


class ModelSpec(BaseModel):
    """Describes a data model. SPEC-04."""

    name: str
    fields: dict[str, str] = {}  # field name → type string ("string", "int", etc.)
    relations: list[str] = []


class ConfigSpec(BaseModel):
    """Describes runtime configuration. SPEC-05."""

    env_vars: dict[str, str] = {}        # var name → description string
    feature_flags: dict[str, bool] = {}  # flag name → default value


class SpecModel(BaseModel):
    """Root model for a declarative YAML spec. SPEC-01 through SPEC-06.

    Only `name` is required; all other fields are optional with sensible
    defaults. Every string field that could represent a language, framework, or
    type is plain str — never Literal or an enum — to satisfy SPEC-06.
    """

    name: str
    version: str = "1.0"
    language: str = ""   # free-form, no constraint — SPEC-06
    framework: str = ""  # free-form, no constraint — SPEC-06
    endpoints: list[EndpointSpec] = []                        # SPEC-02
    components: list[ComponentSpec] = []                      # SPEC-03
    models: list[ModelSpec] = []                              # SPEC-04
    config: ConfigSpec = Field(default_factory=ConfigSpec)    # SPEC-05


def load_spec(path: str | Path) -> SpecModel:
    """Load and validate a YAML spec file, returning a SpecModel.

    Args:
        path: Path to the YAML spec file (str or Path).

    Returns:
        Validated SpecModel instance.

    Raises:
        ValueError: If the file is empty or contains invalid YAML.
        pydantic.ValidationError: If the YAML structure does not match
            SpecModel's schema.
        FileNotFoundError: If the path does not exist.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data:
        raise ValueError(f"Spec file is empty or invalid YAML: {path}")

    return SpecModel(**data)

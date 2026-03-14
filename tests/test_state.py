"""Tests for BuildState — the typed Pydantic state model.

These tests are RED until Plan 03 implements declarative_ai/state.py.
"""
import pytest


def test_buildstate_instantiation(sample_spec_dict):
    """STATE-01: BuildState is created with spec dict; defaults are correct."""
    from declarative_ai.state import BuildState

    state = BuildState(spec=sample_spec_dict)
    assert state.status == "planning"
    assert state.iteration == 0
    assert state.task_graph is None


def test_buildstate_field_validation(sample_spec_dict):
    """STATE-02: BuildState rejects an invalid status string at construction."""
    from declarative_ai.state import BuildState

    with pytest.raises(Exception):  # pydantic.ValidationError
        BuildState(spec=sample_spec_dict, status="invalid-status")


def test_status_transitions_valid(sample_spec_dict):
    """STATE-03: Valid transition chain planning -> building -> validating -> done."""
    from declarative_ai.state import BuildState

    state = BuildState(spec=sample_spec_dict)
    state.transition("building")
    assert state.status == "building"
    state.transition("validating")
    assert state.status == "validating"
    state.transition("done")
    assert state.status == "done"


def test_status_transitions_invalid(sample_spec_dict):
    """STATE-03: Jumping from planning directly to done raises ValidationError."""
    from declarative_ai.state import BuildState

    state = BuildState(spec=sample_spec_dict)
    with pytest.raises(Exception):  # pydantic.ValidationError or ValueError
        state.transition("done")


def test_status_transitions_terminal(sample_spec_dict):
    """STATE-03: A terminal 'done' state cannot transition back to planning."""
    from declarative_ai.state import BuildState

    state = BuildState(spec=sample_spec_dict)
    state.transition("building")
    state.transition("validating")
    state.transition("done")
    with pytest.raises(Exception):  # terminal state — no exit allowed
        state.transition("planning")


def test_buildstate_iteration_tracking(sample_spec_dict):
    """STATE-01: iteration field is mutable and increments correctly."""
    from declarative_ai.state import BuildState

    state = BuildState(spec=sample_spec_dict)
    assert state.iteration == 0
    state.iteration += 1
    assert state.iteration == 1
    state.iteration += 1
    assert state.iteration == 2

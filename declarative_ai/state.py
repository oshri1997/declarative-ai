"""BuildState — shared state Pydantic model with status transition enforcement.

This module provides the BuildState model that is passed by reference through
every phase of the build loop. Status transitions are enforced at the data
layer via the transition() method to prevent invalid state machine moves.
"""
from typing import Optional, Any, Literal

from pydantic import BaseModel, ConfigDict


# Valid transitions: each key -> its set of allowed next values
# Terminal states (done, failed) map to empty sets
_TRANSITIONS: dict[str, set[str]] = {
    "planning":   {"building"},
    "building":   {"validating"},
    "validating": {"done", "failed"},
    "done":       set(),   # terminal
    "failed":     set(),   # terminal
}


class BuildState(BaseModel):
    """Shared state object for the declarative build loop.

    Pass by reference to all agents and the orchestrator loop. Use the
    transition() method to change status — it enforces the allowed graph:
    planning -> building -> validating -> done | failed.

    Direct assignment to status is validated by Pydantic's Literal type
    (rejects unknown strings at construction time). The transition graph
    is enforced by transition().
    """

    model_config = ConfigDict(validate_assignment=True)

    spec: dict[str, Any]
    status: Literal["planning", "building", "validating", "done", "failed"] = "planning"
    iteration: int = 0
    task_graph: Optional[list[dict[str, Any]]] = None
    snapshot: Optional[dict[str, Any]] = None
    gap_report: Optional[dict[str, Any]] = None

    def transition(self, new_status: str) -> None:
        """Perform a status transition with graph validation.

        Raises ValueError if the transition is not allowed from the current
        status (invalid transition or terminal state).

        Valid transitions:
            planning  -> building
            building  -> validating
            validating -> done | failed
            done      -> (terminal, no further transitions)
            failed    -> (terminal, no further transitions)
        """
        current = self.status
        allowed = _TRANSITIONS.get(current, set())
        if new_status not in allowed:
            allowed_display = sorted(allowed) if allowed else ["(terminal state — no transitions allowed)"]
            raise ValueError(
                f"Invalid status transition: {current!r} -> {new_status!r}. "
                f"Allowed from {current!r}: {allowed_display}"
            )
        self.status = new_status

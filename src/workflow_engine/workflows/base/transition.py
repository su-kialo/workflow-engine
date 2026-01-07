"""Transition definition for state machines."""

from dataclasses import dataclass, field
from typing import Awaitable, Callable, Generic, TypeVar

from workflow_engine.workflows.base.event import BaseEventType

E = TypeVar("E", bound=BaseEventType)


@dataclass
class Transition(Generic[E]):
    """Defines a state machine transition.

    A transition specifies:
    - The source state (from_state)
    - The event that triggers the transition (event)
    - The target state (to_state)
    - An optional condition function (is_valid)
    - An optional action callback executed when the transition occurs

    Structure follows: ((from_state, event), to_state)
    """

    from_state: str
    event: E
    to_state: str
    is_valid: Callable[[], bool] | Callable[[], Awaitable[bool]] = field(
        default_factory=lambda: lambda: True
    )
    action: Callable[[], None] | Callable[[], Awaitable[None]] | None = None

    def __repr__(self) -> str:
        return f"Transition({self.from_state!r} --[{self.event.name}]--> {self.to_state!r})"

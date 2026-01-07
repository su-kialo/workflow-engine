"""Abstract state machine base class."""

import inspect
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from workflow_engine.workflows.base.event import BaseEventType
from workflow_engine.workflows.base.state import State
from workflow_engine.workflows.base.transition import Transition

E = TypeVar("E", bound=BaseEventType)


class StateMachineError(Exception):
    """Base exception for state machine errors."""

    pass


class InvalidTransitionError(StateMachineError):
    """Raised when a transition is invalid."""

    pass


class AbstractStateMachine(ABC, Generic[E]):
    """Abstract base class for workflow state machines.

    Subclasses must define:
    - initial_state: The starting state name
    - get_transitions(): Returns list of valid transitions

    The state machine supports:
    - Serialization/deserialization for database persistence
    - Async and sync condition checking
    - Async and sync action callbacks
    """

    def __init__(self, state: State | None = None):
        """Initialize the state machine.

        Args:
            state: Optional initial state. If not provided, uses the
                   initial_state property.
        """
        self._state = state or State(name=self.initial_state, data={})
        self._transitions: list[Transition[E]] = self.get_transitions()

    @property
    @abstractmethod
    def initial_state(self) -> str:
        """Return the initial state name."""
        pass

    @abstractmethod
    def get_transitions(self) -> list[Transition[E]]:
        """Return list of valid transitions for this workflow."""
        pass

    @property
    def state(self) -> State:
        """Get the current state."""
        return self._state

    @property
    def state_name(self) -> str:
        """Get the current state name."""
        return self._state.name

    def get_state_data(self, key: str, default: any = None) -> any:
        """Get a value from state data."""
        return self._state.data.get(key, default)

    def set_state_data(self, key: str, value: any) -> None:
        """Set a value in state data."""
        self._state.data[key] = value

    def get_valid_transitions(self, event: E) -> list[Transition[E]]:
        """Get all transitions valid for current state and event."""
        return [
            t for t in self._transitions if t.from_state == self._state.name and t.event == event
        ]

    def get_available_events(self) -> list[E]:
        """Get all events that could trigger transitions from current state."""
        return list({t.event for t in self._transitions if t.from_state == self._state.name})

    async def advance(self, event: E) -> bool:
        """Attempt to advance the state machine with the given event.

        Args:
            event: The event to process

        Returns:
            True if a transition occurred, False if no valid transition found

        Raises:
            InvalidTransitionError: If the transition conditions are not met
        """
        valid_transitions = self.get_valid_transitions(event)

        if not valid_transitions:
            raise InvalidTransitionError(
                f"No transition defined for event {event.name} in state {self._state.name}"
            )

        for transition in valid_transitions:
            # Check condition
            is_valid_result = transition.is_valid()
            if inspect.isawaitable(is_valid_result):
                is_valid_result = await is_valid_result

            if not is_valid_result:
                continue

            # Execute action if present
            if transition.action:
                action_result = transition.action()
                if inspect.isawaitable(action_result):
                    await action_result

            # Transition to new state
            self._state = State(
                name=transition.to_state,
                data=self._state.data.copy(),
            )
            return True

        raise InvalidTransitionError(
            f"Transition conditions not met for event {event.name} in state {self._state.name}"
        )

    def serialize(self) -> str:
        """Serialize current state to JSON string."""
        return self._state.serialize()

    def to_dict(self) -> dict:
        """Convert current state to dictionary."""
        return self._state.to_dict()

    @classmethod
    def deserialize(cls, json_str: str) -> "AbstractStateMachine[E]":
        """Create state machine instance from serialized state."""
        state = State.deserialize(json_str)
        return cls(state=state)

    @classmethod
    def from_dict(cls, data: dict) -> "AbstractStateMachine[E]":
        """Create state machine instance from dictionary."""
        state = State.from_dict(data)
        return cls(state=state)

"""Pytest configuration and fixtures."""

from enum import Enum

import pytest

from workflow_engine.workflows.base.event import BaseEventType
from workflow_engine.workflows.base.state import State
from workflow_engine.workflows.base.state_machine import AbstractStateMachine
from workflow_engine.workflows.base.transition import Transition


class TestEventType(BaseEventType):
    """Test event types."""

    START = "START"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    DEADLINE = "DEADLINE"
    CANCEL = "CANCEL"


class TestStateMachine(AbstractStateMachine[TestEventType]):
    """Test state machine implementation."""

    @property
    def initial_state(self) -> str:
        return "pending"

    def get_transitions(self) -> list[Transition[TestEventType]]:
        return [
            Transition(
                from_state="pending",
                event=TestEventType.START,
                to_state="in_progress",
            ),
            Transition(
                from_state="in_progress",
                event=TestEventType.APPROVE,
                to_state="approved",
            ),
            Transition(
                from_state="in_progress",
                event=TestEventType.REJECT,
                to_state="rejected",
            ),
            Transition(
                from_state="in_progress",
                event=TestEventType.DEADLINE,
                to_state="expired",
                is_valid=lambda: self.get_state_data("deadline_passed", False),
            ),
            Transition(
                from_state="pending",
                event=TestEventType.CANCEL,
                to_state="cancelled",
            ),
            Transition(
                from_state="in_progress",
                event=TestEventType.CANCEL,
                to_state="cancelled",
            ),
        ]


@pytest.fixture
def test_event_type():
    """Provide the test event type enum."""
    return TestEventType


@pytest.fixture
def test_state_machine():
    """Create a fresh test state machine."""
    return TestStateMachine()


@pytest.fixture
def test_state_machine_class():
    """Provide the test state machine class."""
    return TestStateMachine

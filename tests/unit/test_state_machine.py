"""Tests for state machine functionality."""

import pytest

from workflow_engine.workflows.base.state import State
from workflow_engine.workflows.base.state_machine import InvalidTransitionError


class TestState:
    """Tests for State class."""

    def test_state_creation(self):
        """Test creating a state."""
        state = State(name="test", data={"key": "value"})
        assert state.name == "test"
        assert state.data == {"key": "value"}

    def test_state_default_data(self):
        """Test state with default empty data."""
        state = State(name="test")
        assert state.name == "test"
        assert state.data == {}

    def test_state_serialize(self):
        """Test state serialization."""
        state = State(name="test", data={"count": 5})
        serialized = state.serialize()
        assert '"name": "test"' in serialized
        assert '"count": 5' in serialized

    def test_state_deserialize(self):
        """Test state deserialization."""
        json_str = '{"name": "test", "data": {"count": 5}}'
        state = State.deserialize(json_str)
        assert state.name == "test"
        assert state.data == {"count": 5}

    def test_state_to_dict(self):
        """Test state to dict conversion."""
        state = State(name="test", data={"key": "value"})
        d = state.to_dict()
        assert d == {"name": "test", "data": {"key": "value"}}

    def test_state_from_dict(self):
        """Test state from dict creation."""
        d = {"name": "test", "data": {"key": "value"}}
        state = State.from_dict(d)
        assert state.name == "test"
        assert state.data == {"key": "value"}


class TestStateMachine:
    """Tests for AbstractStateMachine."""

    def test_initial_state(self, test_state_machine):
        """Test that state machine starts in initial state."""
        assert test_state_machine.state_name == "pending"

    def test_valid_transition(self, test_state_machine, test_event_type):
        """Test a valid state transition."""
        import asyncio

        result = asyncio.run(test_state_machine.advance(test_event_type.START))
        assert result is True
        assert test_state_machine.state_name == "in_progress"

    def test_invalid_transition(self, test_state_machine, test_event_type):
        """Test that invalid transitions raise an error."""
        import asyncio

        # APPROVE is not valid from pending state
        with pytest.raises(InvalidTransitionError):
            asyncio.run(test_state_machine.advance(test_event_type.APPROVE))

    def test_multiple_transitions(self, test_state_machine, test_event_type):
        """Test multiple consecutive transitions."""
        import asyncio

        asyncio.run(test_state_machine.advance(test_event_type.START))
        assert test_state_machine.state_name == "in_progress"

        asyncio.run(test_state_machine.advance(test_event_type.APPROVE))
        assert test_state_machine.state_name == "approved"

    def test_conditional_transition_fails(self, test_state_machine, test_event_type):
        """Test that conditional transitions fail when condition is not met."""
        import asyncio

        asyncio.run(test_state_machine.advance(test_event_type.START))

        # DEADLINE transition requires deadline_passed to be True
        with pytest.raises(InvalidTransitionError):
            asyncio.run(test_state_machine.advance(test_event_type.DEADLINE))

    def test_conditional_transition_succeeds(self, test_state_machine, test_event_type):
        """Test that conditional transitions succeed when condition is met."""
        import asyncio

        asyncio.run(test_state_machine.advance(test_event_type.START))
        test_state_machine.set_state_data("deadline_passed", True)

        result = asyncio.run(test_state_machine.advance(test_event_type.DEADLINE))
        assert result is True
        assert test_state_machine.state_name == "expired"

    def test_serialize_deserialize(self, test_state_machine_class, test_event_type):
        """Test serialization and deserialization."""
        import asyncio

        sm = test_state_machine_class()
        asyncio.run(sm.advance(test_event_type.START))
        sm.set_state_data("custom_key", "custom_value")

        # Serialize
        serialized = sm.serialize()

        # Deserialize into new instance
        sm2 = test_state_machine_class.deserialize(serialized)

        assert sm2.state_name == "in_progress"
        assert sm2.get_state_data("custom_key") == "custom_value"

    def test_get_available_events(self, test_state_machine, test_event_type):
        """Test getting available events from current state."""
        events = test_state_machine.get_available_events()
        event_names = {e.name for e in events}
        assert "START" in event_names
        assert "CANCEL" in event_names
        assert "APPROVE" not in event_names

    def test_state_data_preserved(self, test_state_machine, test_event_type):
        """Test that state data is preserved across transitions."""
        import asyncio

        test_state_machine.set_state_data("test_key", "test_value")
        asyncio.run(test_state_machine.advance(test_event_type.START))

        assert test_state_machine.get_state_data("test_key") == "test_value"

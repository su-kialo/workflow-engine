"""Serializable state representation."""

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class State:
    """Represents the current state of a workflow state machine.

    The state includes both the state name and any additional data
    that needs to be persisted with the state.
    """

    name: str
    data: dict[str, Any] = field(default_factory=dict)

    def serialize(self) -> str:
        """Serialize state to JSON string for database storage."""
        return json.dumps({"name": self.name, "data": self.data})

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary."""
        return {"name": self.name, "data": self.data}

    @classmethod
    def deserialize(cls, json_str: str) -> "State":
        """Create a State instance from a JSON string."""
        data = json.loads(json_str)
        return cls(name=data["name"], data=data.get("data", {}))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "State":
        """Create a State instance from a dictionary."""
        return cls(name=data["name"], data=data.get("data", {}))

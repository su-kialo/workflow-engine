"""Workflow registration and discovery."""

from typing import Type

from workflow_engine.workflows.base.state_machine import AbstractStateMachine
from workflow_engine.workflows.classifiers.base import AbstractClassifier


class WorkflowDefinition:
    """Bundles a state machine with its classifier.

    A workflow definition contains everything needed to process
    a specific type of workflow request.
    """

    def __init__(
        self,
        name: str,
        state_machine_class: Type[AbstractStateMachine],
        classifier: AbstractClassifier,
        enabled: bool = True,
    ):
        """Initialize a workflow definition.

        Args:
            name: Unique name for this workflow
            state_machine_class: The state machine class to instantiate
            classifier: The classifier instance for email classification
            enabled: Whether this workflow is currently enabled
        """
        self.name = name
        self.state_machine_class = state_machine_class
        self.classifier = classifier
        self.enabled = enabled

    def create_state_machine(self) -> AbstractStateMachine:
        """Create a new instance of the state machine."""
        return self.state_machine_class()

    def __repr__(self) -> str:
        status = "enabled" if self.enabled else "disabled"
        return f"WorkflowDefinition({self.name!r}, {status})"


class WorkflowRegistry:
    """Central registry for all workflow types.

    Workflows register themselves here for discovery by the
    application. The registry is used to:
    - Find the appropriate workflow for a request type
    - List available workflows
    - Enable/disable workflows
    """

    _workflows: dict[str, WorkflowDefinition] = {}

    @classmethod
    def register(cls, definition: WorkflowDefinition) -> None:
        """Register a workflow definition.

        Args:
            definition: The workflow definition to register
        """
        cls._workflows[definition.name] = definition

    @classmethod
    def unregister(cls, name: str) -> bool:
        """Unregister a workflow by name.

        Args:
            name: The workflow name to unregister

        Returns:
            True if the workflow was found and removed, False otherwise
        """
        if name in cls._workflows:
            del cls._workflows[name]
            return True
        return False

    @classmethod
    def get(cls, name: str) -> WorkflowDefinition | None:
        """Get a workflow by name.

        Args:
            name: The workflow name

        Returns:
            The workflow definition, or None if not found
        """
        return cls._workflows.get(name)

    @classmethod
    def list_all(cls) -> list[WorkflowDefinition]:
        """List all registered workflows."""
        return list(cls._workflows.values())

    @classmethod
    def list_enabled(cls) -> list[WorkflowDefinition]:
        """List only enabled workflows."""
        return [w for w in cls._workflows.values() if w.enabled]

    @classmethod
    def enable(cls, name: str) -> bool:
        """Enable a workflow.

        Args:
            name: The workflow name

        Returns:
            True if the workflow was found and enabled, False otherwise
        """
        if name in cls._workflows:
            cls._workflows[name].enabled = True
            return True
        return False

    @classmethod
    def disable(cls, name: str) -> bool:
        """Disable a workflow.

        Args:
            name: The workflow name

        Returns:
            True if the workflow was found and disabled, False otherwise
        """
        if name in cls._workflows:
            cls._workflows[name].enabled = False
            return True
        return False

    @classmethod
    def clear(cls) -> None:
        """Clear all registered workflows. Useful for testing."""
        cls._workflows.clear()

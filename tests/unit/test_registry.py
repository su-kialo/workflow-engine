"""Tests for workflow registry."""

import pytest

from workflow_engine.workflows.classifiers.keyword import KeywordClassifier
from workflow_engine.workflows.registry import WorkflowDefinition, WorkflowRegistry


class TestWorkflowDefinition:
    """Tests for WorkflowDefinition."""

    def test_definition_creation(self, test_state_machine_class, test_event_type):
        """Test creating a workflow definition."""
        classifier = KeywordClassifier(
            {
                "approved": test_event_type.APPROVE,
            }
        )

        definition = WorkflowDefinition(
            name="test_workflow",
            state_machine_class=test_state_machine_class,
            classifier=classifier,
        )

        assert definition.name == "test_workflow"
        assert definition.enabled is True
        assert definition.state_machine_class == test_state_machine_class

    def test_definition_disabled(self, test_state_machine_class, test_event_type):
        """Test creating a disabled workflow definition."""
        classifier = KeywordClassifier({})

        definition = WorkflowDefinition(
            name="test_workflow",
            state_machine_class=test_state_machine_class,
            classifier=classifier,
            enabled=False,
        )

        assert definition.enabled is False

    def test_create_state_machine(self, test_state_machine_class, test_event_type):
        """Test creating a state machine from definition."""
        classifier = KeywordClassifier({})

        definition = WorkflowDefinition(
            name="test_workflow",
            state_machine_class=test_state_machine_class,
            classifier=classifier,
        )

        sm = definition.create_state_machine()
        assert sm.state_name == "pending"


class TestWorkflowRegistry:
    """Tests for WorkflowRegistry."""

    @pytest.fixture(autouse=True)
    def clear_registry(self):
        """Clear the registry before each test."""
        WorkflowRegistry.clear()
        yield
        WorkflowRegistry.clear()

    def test_register_workflow(self, test_state_machine_class, test_event_type):
        """Test registering a workflow."""
        classifier = KeywordClassifier({})
        definition = WorkflowDefinition(
            name="test_workflow",
            state_machine_class=test_state_machine_class,
            classifier=classifier,
        )

        WorkflowRegistry.register(definition)

        retrieved = WorkflowRegistry.get("test_workflow")
        assert retrieved is not None
        assert retrieved.name == "test_workflow"

    def test_get_nonexistent_workflow(self):
        """Test getting a workflow that doesn't exist."""
        result = WorkflowRegistry.get("nonexistent")
        assert result is None

    def test_list_all_workflows(self, test_state_machine_class, test_event_type):
        """Test listing all workflows."""
        classifier = KeywordClassifier({})

        for i in range(3):
            definition = WorkflowDefinition(
                name=f"workflow_{i}",
                state_machine_class=test_state_machine_class,
                classifier=classifier,
            )
            WorkflowRegistry.register(definition)

        all_workflows = WorkflowRegistry.list_all()
        assert len(all_workflows) == 3

    def test_list_enabled_workflows(self, test_state_machine_class, test_event_type):
        """Test listing only enabled workflows."""
        classifier = KeywordClassifier({})

        # Register enabled workflow
        WorkflowRegistry.register(
            WorkflowDefinition(
                name="enabled_workflow",
                state_machine_class=test_state_machine_class,
                classifier=classifier,
                enabled=True,
            )
        )

        # Register disabled workflow
        WorkflowRegistry.register(
            WorkflowDefinition(
                name="disabled_workflow",
                state_machine_class=test_state_machine_class,
                classifier=classifier,
                enabled=False,
            )
        )

        enabled = WorkflowRegistry.list_enabled()
        assert len(enabled) == 1
        assert enabled[0].name == "enabled_workflow"

    def test_enable_workflow(self, test_state_machine_class, test_event_type):
        """Test enabling a workflow."""
        classifier = KeywordClassifier({})
        definition = WorkflowDefinition(
            name="test_workflow",
            state_machine_class=test_state_machine_class,
            classifier=classifier,
            enabled=False,
        )
        WorkflowRegistry.register(definition)

        result = WorkflowRegistry.enable("test_workflow")
        assert result is True

        workflow = WorkflowRegistry.get("test_workflow")
        assert workflow.enabled is True

    def test_disable_workflow(self, test_state_machine_class, test_event_type):
        """Test disabling a workflow."""
        classifier = KeywordClassifier({})
        definition = WorkflowDefinition(
            name="test_workflow",
            state_machine_class=test_state_machine_class,
            classifier=classifier,
            enabled=True,
        )
        WorkflowRegistry.register(definition)

        result = WorkflowRegistry.disable("test_workflow")
        assert result is True

        workflow = WorkflowRegistry.get("test_workflow")
        assert workflow.enabled is False

    def test_enable_nonexistent_workflow(self):
        """Test enabling a workflow that doesn't exist."""
        result = WorkflowRegistry.enable("nonexistent")
        assert result is False

    def test_disable_nonexistent_workflow(self):
        """Test disabling a workflow that doesn't exist."""
        result = WorkflowRegistry.disable("nonexistent")
        assert result is False

    def test_unregister_workflow(self, test_state_machine_class, test_event_type):
        """Test unregistering a workflow."""
        classifier = KeywordClassifier({})
        definition = WorkflowDefinition(
            name="test_workflow",
            state_machine_class=test_state_machine_class,
            classifier=classifier,
        )
        WorkflowRegistry.register(definition)

        result = WorkflowRegistry.unregister("test_workflow")
        assert result is True
        assert WorkflowRegistry.get("test_workflow") is None

    def test_unregister_nonexistent_workflow(self):
        """Test unregistering a workflow that doesn't exist."""
        result = WorkflowRegistry.unregister("nonexistent")
        assert result is False

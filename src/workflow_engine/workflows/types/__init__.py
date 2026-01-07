"""Workflow type implementations.

This package contains specific workflow implementations.
Each workflow should be in its own module and register itself
with the WorkflowRegistry.

Example workflow structure:
    workflows/types/gdpr_data_request/
        __init__.py
        events.py
        state_machine.py
        classifier.py
        actions.py
"""

"""Application entry point."""

from workflow_engine.api.app import create_app

# Create the FastAPI application
app = create_app()

# Import workflow types to register them
# from workflow_engine.workflows.types import *  # noqa: F401, F403

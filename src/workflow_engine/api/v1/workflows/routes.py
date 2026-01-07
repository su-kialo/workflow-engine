"""Workflow API routes."""

from fastapi import APIRouter, HTTPException, status

from workflow_engine.api.dependencies import CurrentUser
from workflow_engine.api.v1.workflows.schemas import (
    WorkflowListResponse,
    WorkflowResponse,
    WorkflowToggleRequest,
)
from workflow_engine.workflows.registry import WorkflowRegistry

router = APIRouter()


@router.get("", response_model=WorkflowListResponse)
async def list_workflows(
    current_user: CurrentUser,
) -> dict:
    """List all registered workflows."""
    workflows = WorkflowRegistry.list_all()
    return {"workflows": [WorkflowResponse(name=w.name, enabled=w.enabled) for w in workflows]}


@router.get("/{workflow_name}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_name: str,
    current_user: CurrentUser,
) -> WorkflowResponse:
    """Get a specific workflow by name."""
    workflow = WorkflowRegistry.get(workflow_name)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow '{workflow_name}' not found",
        )

    return WorkflowResponse(name=workflow.name, enabled=workflow.enabled)


@router.patch("/{workflow_name}", response_model=WorkflowResponse)
async def toggle_workflow(
    workflow_name: str,
    request: WorkflowToggleRequest,
    current_user: CurrentUser,
) -> WorkflowResponse:
    """Enable or disable a workflow."""
    workflow = WorkflowRegistry.get(workflow_name)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow '{workflow_name}' not found",
        )

    if request.enabled:
        WorkflowRegistry.enable(workflow_name)
    else:
        WorkflowRegistry.disable(workflow_name)

    return WorkflowResponse(name=workflow_name, enabled=request.enabled)

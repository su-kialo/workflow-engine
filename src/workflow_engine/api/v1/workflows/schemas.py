"""Workflow API schemas."""

from pydantic import BaseModel


class WorkflowResponse(BaseModel):
    """Schema for workflow response."""

    name: str
    enabled: bool


class WorkflowListResponse(BaseModel):
    """Schema for workflow list response."""

    workflows: list[WorkflowResponse]


class WorkflowToggleRequest(BaseModel):
    """Schema for enabling/disabling a workflow."""

    enabled: bool

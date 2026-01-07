"""API v1 router aggregating all v1 routes."""

from fastapi import APIRouter

from workflow_engine.api.v1.requests.routes import router as requests_router
from workflow_engine.api.v1.workflows.routes import router as workflows_router

router = APIRouter()

router.include_router(requests_router, prefix="/requests", tags=["Requests"])
router.include_router(workflows_router, prefix="/workflows", tags=["Workflows"])

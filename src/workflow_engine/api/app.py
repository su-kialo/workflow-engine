"""FastAPI application factory."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from workflow_engine.admin.app import router as admin_router
from workflow_engine.api.auth.routes import router as auth_router
from workflow_engine.api.v1.router import router as v1_router
from workflow_engine.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Email Workflow Engine",
        description="API for managing email workflow requests",
        version="0.1.0",
        debug=settings.debug,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount admin static files
    static_dir = Path(__file__).parent.parent / "admin" / "static"
    app.mount("/admin/static", StaticFiles(directory=str(static_dir)), name="admin_static")

    # Include routers
    app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    app.include_router(v1_router, prefix="/api/v1")
    app.include_router(admin_router, prefix="/admin", tags=["Admin"])

    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint."""
        return {"status": "healthy"}

    return app

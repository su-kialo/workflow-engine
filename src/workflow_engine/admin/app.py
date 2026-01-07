"""Admin interface routes."""

from pathlib import Path

from fastapi import APIRouter, Form, Query, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select

from workflow_engine.admin.auth import (
    AdminSession,
    clear_session,
    create_session,
    get_session,
    verify_admin_password,
)
from workflow_engine.config import get_settings
from workflow_engine.db.models import Request as RequestModel
from workflow_engine.db.models.enums import RequestStatus
from workflow_engine.db.session import AsyncSessionLocal
from workflow_engine.worker.celery_app import celery_app
from workflow_engine.workflows.registry import WorkflowRegistry

# Set up templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> HTMLResponse:
    """Render the login page."""
    # If already logged in, redirect to dashboard
    if get_session(request):
        return RedirectResponse(url="/admin/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None},
    )


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
) -> Response:
    """Process login form."""
    settings = get_settings()

    # Validate credentials
    if username != settings.admin_username or not verify_admin_password(password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Create session and redirect
    redirect = RedirectResponse(url="/admin/", status_code=status.HTTP_303_SEE_OTHER)
    create_session(redirect, username)
    return redirect


@router.get("/logout")
async def logout(response: Response) -> RedirectResponse:
    """Log out and redirect to login page."""
    redirect = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    clear_session(redirect)
    return redirect


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, session: AdminSession) -> HTMLResponse:
    """Render the admin dashboard."""
    async with AsyncSessionLocal() as db:
        # Get request counts by status
        status_counts = {}
        for req_status in RequestStatus:
            result = await db.execute(
                select(func.count(RequestModel.id)).where(RequestModel.status == req_status)
            )
            status_counts[req_status.value] = result.scalar_one()

        total_requests = sum(status_counts.values())

    # Get workflow counts
    workflows = WorkflowRegistry.list_all()
    enabled_workflows = len([w for w in workflows if w.enabled])

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "session": session,
            "status_counts": status_counts,
            "total_requests": total_requests,
            "total_workflows": len(workflows),
            "enabled_workflows": enabled_workflows,
        },
    )


@router.get("/requests", response_class=HTMLResponse)
async def requests_list(
    request: Request,
    session: AdminSession,
    page: int = Query(1, ge=1),
    status_filter: str | None = Query(None),
) -> HTMLResponse:
    """Render the requests list page."""
    page_size = 20
    offset = (page - 1) * page_size

    async with AsyncSessionLocal() as db:
        # Build query
        query = select(RequestModel)
        count_query = select(func.count(RequestModel.id))

        if status_filter:
            try:
                filter_status = RequestStatus(status_filter)
                query = query.where(RequestModel.status == filter_status)
                count_query = count_query.where(RequestModel.status == filter_status)
            except ValueError:
                pass

        # Get total count
        count_result = await db.execute(count_query)
        total = count_result.scalar_one()

        # Get paginated results
        query = query.order_by(RequestModel.created_at.desc()).offset(offset).limit(page_size)
        result = await db.execute(query)
        requests = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return templates.TemplateResponse(
        "requests/list.html",
        {
            "request": request,
            "session": session,
            "requests": requests,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "status_filter": status_filter,
            "statuses": [s.value for s in RequestStatus],
        },
    )


@router.get("/requests/{request_id}", response_class=HTMLResponse)
async def request_detail(
    request: Request,
    request_id: int,
    session: AdminSession,
) -> HTMLResponse:
    """Render the request detail page."""
    async with AsyncSessionLocal() as db:
        req = await db.get(RequestModel, request_id)
        if not req:
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": "Request not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

    return templates.TemplateResponse(
        "requests/detail.html",
        {
            "request": request,
            "session": session,
            "req": req,
        },
    )


@router.get("/jobs", response_class=HTMLResponse)
async def jobs_page(request: Request, session: AdminSession) -> HTMLResponse:
    """Render the jobs management page."""
    return templates.TemplateResponse(
        "jobs/trigger.html",
        {
            "request": request,
            "session": session,
            "message": None,
        },
    )


@router.post("/jobs/trigger/{job_name}")
async def trigger_job(
    request: Request,
    job_name: str,
    session: AdminSession,
) -> HTMLResponse:
    """Trigger a background job manually."""
    valid_jobs = {
        "process_inbound": "workflow_engine.worker.tasks.process_inbound_emails.process_inbound",
        "check_deadlines": "workflow_engine.worker.tasks.check_deadlines.check_deadline_conditions",
    }

    if job_name not in valid_jobs:
        return templates.TemplateResponse(
            "jobs/trigger.html",
            {
                "request": request,
                "session": session,
                "message": {"type": "error", "text": f"Unknown job: {job_name}"},
            },
        )

    # Trigger the task
    task_name = valid_jobs[job_name]
    celery_app.send_task(task_name)

    return templates.TemplateResponse(
        "jobs/trigger.html",
        {
            "request": request,
            "session": session,
            "message": {"type": "success", "text": f"Job '{job_name}' triggered successfully"},
        },
    )

"""Request API routes."""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from workflow_engine.api.dependencies import CurrentUser, DBSession
from workflow_engine.api.v1.requests.schemas import (
    RequestCreate,
    RequestCreateWithClient,
    RequestDetailResponse,
    RequestListResponse,
    RequestResponse,
    RequestStateResponse,
)
from workflow_engine.db.models import Client, Request, RequestStateHistory

router = APIRouter()


@router.post("", response_model=RequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    request_data: RequestCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> Request:
    """Create a new request for an existing client."""
    # Verify client exists
    client = await db.get(Client, request_data.client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id {request_data.client_id} not found",
        )

    # Create the request
    request = Request(
        client_id=request_data.client_id,
        type=request_data.type,
        target_name=request_data.target_name,
        target_email=request_data.target_email,
        target_responsible_name=request_data.target_responsible_name,
    )
    db.add(request)
    await db.flush()
    await db.refresh(request)

    return request


@router.post(
    "/with-client",
    response_model=RequestDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_request_with_client(
    request_data: RequestCreateWithClient,
    db: DBSession,
    current_user: CurrentUser,
) -> Request:
    """Create a new request with a new client."""
    # Check if client email already exists
    existing_client = await db.execute(
        select(Client).where(Client.email == request_data.client.email)
    )
    if existing_client.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Client with email {request_data.client.email} already exists",
        )

    # Create the client
    client = Client(
        name=request_data.client.name,
        email=request_data.client.email,
        phone=request_data.client.phone,
        address=request_data.client.address,
        notes=request_data.client.notes,
    )
    db.add(client)
    await db.flush()

    # Create the request
    request = Request(
        client_id=client.id,
        type=request_data.type,
        target_name=request_data.target_name,
        target_email=request_data.target_email,
        target_responsible_name=request_data.target_responsible_name,
    )
    db.add(request)
    await db.flush()
    await db.refresh(request)

    return request


@router.get("", response_model=RequestListResponse)
async def list_requests(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    """List all requests with pagination."""
    offset = (page - 1) * page_size

    # Get total count
    count_result = await db.execute(select(func.count(Request.id)))
    total = count_result.scalar_one()

    # Get paginated results
    result = await db.execute(
        select(Request).order_by(Request.created_at.desc()).offset(offset).limit(page_size)
    )
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{request_id}", response_model=RequestDetailResponse)
async def get_request(
    request_id: int,
    db: DBSession,
    current_user: CurrentUser,
) -> Request:
    """Get a specific request by ID."""
    request = await db.get(Request, request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with id {request_id} not found",
        )

    return request


@router.get("/{request_id}/state", response_model=RequestStateResponse)
async def get_request_state(
    request_id: int,
    db: DBSession,
    current_user: CurrentUser,
) -> dict:
    """Get the current state of a request's workflow."""
    request = await db.get(Request, request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request with id {request_id} not found",
        )

    # Get the latest state history entry
    result = await db.execute(
        select(RequestStateHistory)
        .where(RequestStateHistory.request_id == request_id)
        .order_by(RequestStateHistory.created_at.desc())
        .limit(1)
    )
    state_history = result.scalar_one_or_none()

    current_state = {}
    if state_history:
        current_state = state_history.request_state_data

    return {
        "request_id": request_id,
        "current_state": current_state,
        "status": request.status,
    }

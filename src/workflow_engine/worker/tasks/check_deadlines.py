"""Task for checking deadline conditions."""

import asyncio
from datetime import datetime, timezone

import structlog
from sqlalchemy import select

from workflow_engine.db.models import Request, RequestStateHistory
from workflow_engine.db.models.enums import RequestStatus
from workflow_engine.db.session import AsyncSessionLocal
from workflow_engine.worker.celery_app import celery_app
from workflow_engine.workflows.registry import WorkflowRegistry

logger = structlog.get_logger()


async def _check_deadline_conditions() -> dict:
    """Check all open requests for deadline-based transitions.

    Returns:
        Dictionary with processing statistics
    """
    stats = {
        "requests_checked": 0,
        "deadlines_triggered": 0,
        "errors": 0,
    }

    async with AsyncSessionLocal() as session:
        # Get all open requests
        result = await session.execute(
            select(Request).where(
                Request.status.not_in([RequestStatus.COMPLETED, RequestStatus.CANCELLED])
            )
        )
        open_requests = result.scalars().all()

        for request in open_requests:
            stats["requests_checked"] += 1

            try:
                # Get the workflow for this request type
                workflow_def = WorkflowRegistry.get(request.type.value)
                if not workflow_def:
                    continue

                if not workflow_def.enabled:
                    continue

                # Get the current state
                state_result = await session.execute(
                    select(RequestStateHistory)
                    .where(RequestStateHistory.request_id == request.id)
                    .order_by(RequestStateHistory.created_at.desc())
                    .limit(1)
                )
                current_state_record = state_result.scalar_one_or_none()

                if not current_state_record:
                    continue

                # Create state machine from current state
                state_machine = workflow_def.state_machine_class.from_dict(
                    current_state_record.request_state_data
                )

                # Check for deadline in state data
                deadline_at = state_machine.get_state_data("deadline_at")
                if not deadline_at:
                    continue

                # Parse deadline if it's a string
                if isinstance(deadline_at, str):
                    deadline_at = datetime.fromisoformat(deadline_at)

                # Check if deadline has passed
                now = datetime.now(timezone.utc)
                if deadline_at > now:
                    continue

                logger.info(
                    "Deadline reached",
                    request_id=request.id,
                    deadline_at=deadline_at.isoformat(),
                )

                # Get available events and try deadline-related ones
                available_events = state_machine.get_available_events()
                deadline_triggered = False

                for event in available_events:
                    # Look for deadline-related events
                    # Convention: deadline events should have "DEADLINE" in the name
                    if "DEADLINE" in event.name.upper():
                        try:
                            advanced = await state_machine.advance(event)
                            if advanced:
                                deadline_triggered = True
                                stats["deadlines_triggered"] += 1

                                # Save new state
                                new_state_history = RequestStateHistory(
                                    request_id=request.id,
                                    request_state_data=state_machine.to_dict(),
                                )
                                session.add(new_state_history)

                                logger.info(
                                    "Deadline transition completed",
                                    request_id=request.id,
                                    event=event.name,
                                    new_state=state_machine.state_name,
                                )
                                break
                        except Exception as e:
                            logger.debug(
                                "Deadline event not valid",
                                request_id=request.id,
                                event=event.name,
                                error=str(e),
                            )

                if not deadline_triggered:
                    logger.debug(
                        "No valid deadline transition found",
                        request_id=request.id,
                        current_state=state_machine.state_name,
                    )

            except Exception as e:
                stats["errors"] += 1
                logger.error(
                    "Error checking deadline for request",
                    request_id=request.id,
                    error=str(e),
                )

        await session.commit()

    return stats


@celery_app.task(name="workflow_engine.worker.tasks.check_deadlines.check_deadline_conditions")
def check_deadline_conditions() -> dict:
    """Celery task to check deadline conditions.

    Returns:
        Dictionary with processing statistics
    """
    logger.info("Starting deadline condition check")
    result = asyncio.run(_check_deadline_conditions())
    logger.info("Completed deadline condition check", **result)
    return result

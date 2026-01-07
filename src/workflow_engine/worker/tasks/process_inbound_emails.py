"""Task for processing inbound emails."""

import asyncio

import structlog

from workflow_engine.db.models import Request, RequestEmailLog, RequestStateHistory
from workflow_engine.db.models.enums import RequestStatus
from workflow_engine.db.session import AsyncSessionLocal
from workflow_engine.email.receiver import EmailReceiver
from workflow_engine.email.ses import SESEmailProvider
from workflow_engine.worker.celery_app import celery_app
from workflow_engine.workflows.registry import WorkflowRegistry

logger = structlog.get_logger()


async def _process_inbound_emails() -> dict:
    """Process inbound emails and advance workflows.

    Returns:
        Dictionary with processing statistics
    """
    stats = {
        "emails_processed": 0,
        "emails_matched": 0,
        "workflows_advanced": 0,
        "errors": 0,
    }

    # Initialize email receiver
    # Note: S3 bucket should be configured for production
    provider = SESEmailProvider(s3_bucket=None)
    receiver = EmailReceiver(provider)

    # Fetch and group emails by request ID
    try:
        grouped_emails = await receiver.fetch_and_group_by_request()
    except Exception as e:
        logger.error("Failed to fetch emails", error=str(e))
        return stats

    async with AsyncSessionLocal() as session:
        for request_id, emails in grouped_emails.items():
            for email_message in emails:
                stats["emails_processed"] += 1

                try:
                    # Get the request
                    request = await session.get(Request, request_id)
                    if not request:
                        logger.warning(
                            "Request not found for email",
                            request_id=request_id,
                            subject=email_message.subject,
                        )
                        continue

                    stats["emails_matched"] += 1

                    # Skip if request is already completed or cancelled
                    if request.status in [
                        RequestStatus.COMPLETED,
                        RequestStatus.CANCELLED,
                    ]:
                        logger.info(
                            "Skipping email for closed request",
                            request_id=request_id,
                            status=request.status.value,
                        )
                        await receiver.mark_processed(email_message.message_id)
                        continue

                    # Get the workflow for this request type
                    workflow_def = WorkflowRegistry.get(request.type.value)
                    if not workflow_def:
                        logger.warning(
                            "No workflow registered for request type",
                            request_id=request_id,
                            request_type=request.type.value,
                        )
                        continue

                    if not workflow_def.enabled:
                        logger.info(
                            "Workflow is disabled",
                            workflow=workflow_def.name,
                        )
                        continue

                    # Get the current state
                    state_history = await session.execute(
                        session.query(RequestStateHistory)
                        .filter(RequestStateHistory.request_id == request_id)
                        .order_by(RequestStateHistory.created_at.desc())
                        .limit(1)
                    )
                    current_state_record = state_history.scalar_one_or_none()

                    # Create state machine from current state
                    if current_state_record:
                        state_machine = workflow_def.state_machine_class.from_dict(
                            current_state_record.request_state_data
                        )
                    else:
                        state_machine = workflow_def.create_state_machine()

                    event = await workflow_def.classifier.classify_async(email_message.body_text)

                    if event is None:
                        logger.info(
                            "Could not classify email",
                            request_id=request_id,
                            subject=email_message.subject,
                        )
                        continue

                    # Try to advance the state machine
                    try:
                        advanced = await state_machine.advance(event)
                        if advanced:
                            stats["workflows_advanced"] += 1

                            # Save new state
                            new_state_history = RequestStateHistory(
                                request_id=request_id,
                                request_state_data=state_machine.to_dict(),
                            )
                            session.add(new_state_history)

                            # Update request status based on state
                            # This could be customized per workflow
                            request.last_response_at = email_message.received_at

                            logger.info(
                                "Workflow advanced",
                                request_id=request_id,
                                new_state=state_machine.state_name,
                            )
                    except Exception as e:
                        logger.warning(
                            "Failed to advance workflow",
                            request_id=request_id,
                            event=event.name,
                            error=str(e),
                        )

                    # Log the email
                    email_log = RequestEmailLog(
                        request_id=request_id,
                        is_outgoing=False,
                        email_subject=email_message.subject,
                        email_body=email_message.body_text,
                    )
                    session.add(email_log)

                    # Mark email as processed
                    await receiver.mark_processed(email_message.message_id)

                except Exception as e:
                    stats["errors"] += 1
                    logger.error(
                        "Error processing email",
                        request_id=request_id,
                        error=str(e),
                    )

        await session.commit()

    return stats


@celery_app.task(name="workflow_engine.worker.tasks.process_inbound_emails.process_inbound")
def process_inbound() -> dict:
    """Celery task to process inbound emails.

    Returns:
        Dictionary with processing statistics
    """
    logger.info("Starting inbound email processing")
    result = asyncio.run(_process_inbound_emails())
    logger.info("Completed inbound email processing", **result)
    return result

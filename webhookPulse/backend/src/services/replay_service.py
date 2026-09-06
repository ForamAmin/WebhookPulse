from fastapi import HTTPException, status

from src.repositories.event_repository import (
    get_event_by_id,
    update_event_status,
)
from src.services.queue_service import enqueue_event


def replay_event(event_id: str, tenant_id: str):
    event = get_event_by_id(
        event_id=event_id,
        tenant_id=tenant_id,
    )

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event["status"] != "dlq":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only DLQ events can be replayed",
        )

    update_event_status(
        event_id=event_id,
        tenant_id=tenant_id,
        status="queued",
        attempt_count=0,
    )

    message_id = enqueue_event(event)

    return {
        "event_id": event_id,
        "correlation_id": event["correlation_id"],
        "status": "queued",
        "message_id": message_id,
    }
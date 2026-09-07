from fastapi import HTTPException, status

from src.repositories.event_repository import (
    get_event_details,
    get_events_by_tenant,
    get_event_stats_by_tenant,
)
from src.repositories.delivery_attempt_repository import (
    get_attempts_for_event,
)


def get_event_with_attempts(
    event_id: str,
    tenant_id: str,
):
    event = get_event_details(
        event_id=event_id,
        tenant_id=tenant_id,
    )

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    attempts = get_attempts_for_event(
        event_id=event_id,
        tenant_id=tenant_id,
    )

    event["_id"] = str(event["_id"])

    for attempt in attempts:
        attempt["_id"] = str(attempt["_id"])

    return {
        "event": event,
        "delivery_attempts": attempts,
    }

def list_events(tenant_id: str):
    events = get_events_by_tenant(
        tenant_id=tenant_id,
    )

    for event in events:
        event["_id"] = str(event["_id"])

    return events

def get_event_stats(tenant_id: str):
    return get_event_stats_by_tenant(
        tenant_id=tenant_id,
    )
from src.services.replay_service import replay_event
from src.services.event_service import (
    get_event_with_attempts,
    get_event_stats,
    list_events,
)


def replay(
    event_id: str,
    tenant_id: str,
):
    return replay_event(
        event_id=event_id,
        tenant_id=tenant_id,
    )

def get_event(
    event_id: str,
    tenant_id: str,
):
    return get_event_with_attempts(
        event_id=event_id,
        tenant_id=tenant_id,
    )

def get_events(tenant_id: str):
    return list_events(
        tenant_id=tenant_id,
    )

def get_stats(tenant_id: str):
    return get_event_stats(
        tenant_id=tenant_id,
    )
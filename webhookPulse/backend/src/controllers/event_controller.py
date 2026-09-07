from src.services.replay_service import replay_event


def replay(
    event_id: str,
    tenant_id: str,
):
    return replay_event(
        event_id=event_id,
        tenant_id=tenant_id,
    )
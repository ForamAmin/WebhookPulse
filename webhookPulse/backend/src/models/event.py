from datetime import datetime, timezone


def create_event_document(
    event_id: str,
    tenant_id: str,
    endpoint_id: str,
    provider: str,
    provider_event_id: str | None,
    dedupe_key: str,
    event_type: str | None,
    correlation_id: str,
    payload: dict,
) -> dict:
    now = datetime.now(timezone.utc)

    return {
        "event_id": event_id,
        "tenant_id": tenant_id,
        "endpoint_id": endpoint_id,
        "provider": provider,
        "provider_event_id": provider_event_id,
        "dedupe_key": dedupe_key,
        "event_type": event_type,
        "correlation_id": correlation_id,
        "payload": payload,
        "status": "received",
        "attempt_count": 0,
        "received_at": now,
        "created_at": now,
        "updated_at": now,
    }
from datetime import datetime, timezone


def create_delivery_attempt_document(
    attempt_id: str,
    tenant_id: str,
    event_id: str,
    attempt_number: int,
    status_code: int | None,
    response_time_ms: float | None,
    response_body: str | None,
    error: str | None,
    started_at: datetime,
    completed_at: datetime,
) -> dict:
    return {
        "attempt_id": attempt_id,
        "tenant_id": tenant_id,
        "event_id": event_id,
        "attempt_number": attempt_number,
        "status_code": status_code,
        "response_time_ms": response_time_ms,
        "response_body": response_body,
        "error": error,
        "started_at": started_at,
        "completed_at": completed_at,
        "created_at": datetime.now(timezone.utc),
    }
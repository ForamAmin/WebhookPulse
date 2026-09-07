from src.infrastructure.redis import redis_client, WEBHOOK_STREAM


def enqueue_event(event: dict):
    message = {
        "event_id": event["event_id"],
        "tenant_id": event["tenant_id"],
        "endpoint_id": event["endpoint_id"],
        "correlation_id": event["correlation_id"],
    }

    return redis_client.xadd(
        WEBHOOK_STREAM,
        message,
    )
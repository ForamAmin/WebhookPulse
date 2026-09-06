from src.infrastructure.redis import redis_client, DLQ_STREAM


def move_to_dlq(event: dict):
    return redis_client.xadd(
        DLQ_STREAM,
        {
            "event_id": event["event_id"],
            "tenant_id": event["tenant_id"],
            "endpoint_id": event["endpoint_id"],
            "correlation_id": event["correlation_id"],
        },
    )
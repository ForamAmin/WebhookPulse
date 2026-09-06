import httpx
import redis
import secrets
import time
from datetime import datetime, timezone

from src.infrastructure.redis import redis_client, WEBHOOK_STREAM
from src.repositories.endpoint_repository import get_endpoint_by_id
from src.repositories.event_repository import get_event_by_id
from src.models.delivery_attempt import create_delivery_attempt_document
from src.repositories.delivery_attempt_repository import create_delivery_attempt

def process_event(message_id: str, data: dict):
    event_id = data["event_id"]
    tenant_id = data["tenant_id"]
    endpoint_id = data["endpoint_id"]

    print(f"\nPROCESSING EVENT: {event_id}")
    print(f"Redis message: {message_id}")

    endpoint = get_endpoint_by_id(endpoint_id)

    if not endpoint:
        print(f"Endpoint not found: {endpoint_id}")
        return

    event = get_event_by_id(
        event_id=event_id,
        tenant_id=tenant_id,
    )

    if not event:
        print(f"Event not found: {event_id}")
        return

    destination_url = endpoint["destination_url"]

    print(f"Delivering to: {destination_url}")

    attempt_number = event.get("attempt_count", 0) + 1

    started_at = datetime.now(timezone.utc)
    start_time = time.perf_counter()

    status_code = None
    response_body = None
    error = None

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                destination_url,
                json=event["payload"],
                headers={
                    "X-WebhookPulse-Event-ID": event_id,
                    "X-WebhookPulse-Correlation-ID": event["correlation_id"],
                },
            )

        status_code = response.status_code
        response_body = response.text

        print(f"Destination response: {status_code}")

    except Exception as e:
        error = str(e)
        print(f"Delivery error: {error}")

    end_time = time.perf_counter()
    completed_at = datetime.now(timezone.utc)

    response_time_ms = (end_time - start_time) * 1000

    attempt_document = create_delivery_attempt_document(
        attempt_id=f"att_{secrets.token_urlsafe(16)}",
        tenant_id=tenant_id,
        event_id=event_id,
        attempt_number=attempt_number,
        status_code=status_code,
        response_time_ms=response_time_ms,
        response_body=response_body,
        error=error,
        started_at=started_at,
        completed_at=completed_at,
    )

    print("Saving delivery attempt to MongoDB...")

    try:
        create_delivery_attempt(attempt_document)

        print(
        f"Attempt #{attempt_number} recorded "
        f"({response_time_ms:.2f} ms)"
    )

    except Exception as e:
        print(f"FAILED TO SAVE DELIVERY ATTEMPT: {e}")
        raise   

def run_worker():
    print("WebhookPulse worker started")
    print(f"Listening to stream: {WEBHOOK_STREAM}")

    last_id = "0-0"

    while True:
        try:
            messages = redis_client.xread(
                {
                    WEBHOOK_STREAM: last_id
                },
                block=5000,
                count=1,
            )

            if not messages:
                continue

            for stream_name, stream_messages in messages:
                for message_id, data in stream_messages:

                    try:
                        process_event(
                            message_id=message_id,
                            data=data,
                        )

                        last_id = message_id

                    except Exception as e:
                        print(f"Worker error while processing event: {e}")

        except redis.exceptions.TimeoutError:
            # Redis did not receive a new message during the blocking period.
            # Keep the worker alive and wait again.
            continue

        except Exception as e:
            print(f"Redis worker error: {e}")


if __name__ == "__main__":
    run_worker()
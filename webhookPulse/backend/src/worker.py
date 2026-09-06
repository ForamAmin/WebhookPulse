import json
import redis
import time
from src.repositories.event_repository import get_event_by_id
import httpx

from src.infrastructure.redis import redis_client, WEBHOOK_STREAM
from src.repositories.endpoint_repository import get_endpoint_by_id


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

    payload = event["payload"]

    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            destination_url,
            json=payload,
            headers={
                "X-WebhookPulse-Event-ID": event_id,
                "X-WebhookPulse-Correlation-ID": event["correlation_id"],
            },
        )

    print(f"Destination response: {response.status_code}")

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
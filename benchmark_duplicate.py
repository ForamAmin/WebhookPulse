import asyncio
import hashlib
import hmac
import json

import httpx


BASELINE_URL = "http://127.0.0.1:8000/webhook"

WEBHOOKPULSE_URL = (
    "http://127.0.0.1:8001/"
    "webhooks/ep_TKYKRCdauTN-wYQYYIG8vw"
)

SIGNING_SECRET = "benchmark-secret"


PAYLOAD = {
    "event": "payment.captured",
    "payload": {
        "payment": {
            "entity": {
                "id": "benchmark_duplicate_001",
                "amount": 10000,
                "currency": "INR",
                "status": "captured",
            }
        }
    },
    "benchmark": {
        "run": "duplicate-test",
        "event_number": 1,
    },
}


def create_body():
    return json.dumps(
        PAYLOAD,
        separators=(",", ":"),
    ).encode("utf-8")


def create_signature(body):
    return hmac.new(
        SIGNING_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()


async def send_baseline(client, body):
    response = await client.post(
        BASELINE_URL,
        content=body,
        headers={
            "Content-Type": "application/json",
        },
    )

    return response


async def send_webhookpulse(client, body):
    signature = create_signature(body)

    response = await client.post(
        WEBHOOKPULSE_URL,
        content=body,
        headers={
            "Content-Type": "application/json",
            "x-razorpay-signature": signature,
            "x-razorpay-event-id": "benchmark_duplicate_event_001",
        },
    )

    return response


async def main():

    body = create_body()

    async with httpx.AsyncClient(timeout=10) as client:

        print("=" * 60)
        print("DUPLICATE DELIVERY EXPERIMENT")
        print("=" * 60)

        print("\nBASELINE")
        print("-" * 60)

        response_1 = await send_baseline(client, body)

        print(
            "Delivery #1:",
            response_1.status_code,
            response_1.json(),
        )

        response_2 = await send_baseline(client, body)

        print(
            "Delivery #2:",
            response_2.status_code,
            response_2.json(),
        )

        print("\nWEBHOOKPULSE")
        print("-" * 60)

        response_3 = await send_webhookpulse(client, body)

        print(
            "Delivery #1:",
            response_3.status_code,
            response_3.json(),
        )

        response_4 = await send_webhookpulse(client, body)

        print(
            "Delivery #2:",
            response_4.status_code,
            response_4.json(),
        )

        print("\nDONE")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
import asyncio
import hashlib
import hmac
import json
import statistics
import time
from datetime import datetime, timezone

import httpx


WEBHOOKPULSE_URL = (
    "http://127.0.0.1:8000/"
    "webhooks/ep_TKYKRCdauTN-wYQYYIG8vw"
)

SIGNING_SECRET = "benchmark-secret"

TOTAL_EVENTS = 30


def make_payload(index: int):
    payment_id = f"benchmark_pay_{index:03d}"

    return {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": payment_id,
                    "amount": 10000 + index,
                    "currency": "INR",
                    "status": "captured",
                }
            }
        },
        "benchmark": {
            "run": "webhookpulse-normal",
            "event_number": index,
        },
    }


def generate_signature(raw_body: bytes):
    return hmac.new(
        SIGNING_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()


async def send_event(client, index):
    payload = make_payload(index)

    raw_body = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode("utf-8")

    signature = generate_signature(raw_body)

    # Each benchmark event gets a unique provider event ID.
    provider_event_id = f"benchmark_event_{index:03d}"

    start = time.perf_counter()

    response = await client.post(
        WEBHOOKPULSE_URL,
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "x-razorpay-signature": signature,
            "x-razorpay-event-id": provider_event_id,
        },
    )

    end = time.perf_counter()

    latency_ms = (end - start) * 1000

    try:
        response_body = response.json()
    except Exception:
        response_body = response.text

    return {
        "logical_event": index,
        "provider_event_id": provider_event_id,
        "payment_id": payload["payload"]["payment"]["entity"]["id"],
        "status_code": response.status_code,
        "latency_ms": latency_ms,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "response": response_body,
    }


async def main():
    print("=" * 60)
    print("WebhookPulse Normal Benchmark")
    print("=" * 60)

    print(f"Target: {WEBHOOKPULSE_URL}")
    print(f"Logical events: {TOTAL_EVENTS}")
    print()

    results = []

    async with httpx.AsyncClient(timeout=10) as client:

        for index in range(1, TOTAL_EVENTS + 1):

            result = await send_event(client, index)
            results.append(result)

            print(
                f"Event {index:02d} | "
                f"HTTP {result['status_code']} | "
                f"{result['latency_ms']:.2f} ms"
            )

    successful = [
        r for r in results
        if 200 <= r["status_code"] < 300
    ]

    failed = [
        r for r in results
        if not (200 <= r["status_code"] < 300)
    ]

    latencies = [
        r["latency_ms"]
        for r in results
    ]

    success_rate = (
        len(successful) / TOTAL_EVENTS
    ) * 100

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(f"Logical events sent : {TOTAL_EVENTS}")
    print(f"Successful          : {len(successful)}")
    print(f"Failed              : {len(failed)}")
    print(f"Success rate        : {success_rate:.2f}%")

    if latencies:
        print(f"Average ACK latency : {statistics.mean(latencies):.2f} ms")
        print(f"Median ACK latency  : {statistics.median(latencies):.2f} ms")
        print(f"Min ACK latency     : {min(latencies):.2f} ms")
        print(f"Max ACK latency     : {max(latencies):.2f} ms")

    output_file = "webhookpulse_benchmark_normal.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "benchmark": "webhookpulse-normal",
                "target": WEBHOOKPULSE_URL,
                "total_logical_events": TOTAL_EVENTS,
                "successful": len(successful),
                "failed": len(failed),
                "success_rate_percent": success_rate,
                "average_ack_latency_ms": (
                    statistics.mean(latencies)
                    if latencies
                    else None
                ),
                "median_ack_latency_ms": (
                    statistics.median(latencies)
                    if latencies
                    else None
                ),
                "min_ack_latency_ms": (
                    min(latencies)
                    if latencies
                    else None
                ),
                "max_ack_latency_ms": (
                    max(latencies)
                    if latencies
                    else None
                ),
                "events": results,
            },
            f,
            indent=2,
        )

    print()
    print(f"Raw results saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
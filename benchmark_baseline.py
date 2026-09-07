import asyncio
import hashlib
import json
import statistics
import time
from datetime import datetime, timezone

import httpx


BASELINE_URL = "http://127.0.0.1:8000/webhook"
TOTAL_EVENTS = 30


def make_payload(index: int):
    """
    Create one logical webhook event.

    Each event gets a unique payment ID so we can distinguish
    30 different logical events.
    """
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
            "run": "baseline-normal",
            "event_number": index,
        },
    }


async def send_event(client, index):
    payload = make_payload(index)

    raw_body = json.dumps(payload)

    start = time.perf_counter()

    response = await client.post(
        BASELINE_URL,
        content=raw_body,
        headers={
            "Content-Type": "application/json",
        },
    )

    end = time.perf_counter()

    latency_ms = (end - start) * 1000

    payment_id = (
        payload["payload"]["payment"]["entity"]["id"]
    )

    return {
        "logical_event": index,
        "payment_id": payment_id,
        "status_code": response.status_code,
        "latency_ms": latency_ms,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "response": response.json(),
    }


async def main():
    print("=" * 60)
    print("WebhookPulse Baseline Benchmark")
    print("=" * 60)

    print(f"Target: {BASELINE_URL}")
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

    # ---------------------------------------------------------
    # Calculate benchmark statistics
    # ---------------------------------------------------------

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
        print(f"Average latency     : {statistics.mean(latencies):.2f} ms")
        print(f"Median latency      : {statistics.median(latencies):.2f} ms")
        print(f"Min latency         : {min(latencies):.2f} ms")
        print(f"Max latency         : {max(latencies):.2f} ms")

    # ---------------------------------------------------------
    # Save raw results
    # ---------------------------------------------------------

    output_file = "baseline_benchmark_normal.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "benchmark": "baseline-normal",
                "target": BASELINE_URL,
                "total_logical_events": TOTAL_EVENTS,
                "successful": len(successful),
                "failed": len(failed),
                "success_rate_percent": success_rate,
                "average_latency_ms": (
                    statistics.mean(latencies)
                    if latencies
                    else None
                ),
                "median_latency_ms": (
                    statistics.median(latencies)
                    if latencies
                    else None
                ),
                "min_latency_ms": (
                    min(latencies)
                    if latencies
                    else None
                ),
                "max_latency_ms": (
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
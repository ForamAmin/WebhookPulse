from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse


router = APIRouter(
    prefix="/test-receiver",
    tags=["Test Receiver"],
)


@router.post("/success")
async def success_receiver(request: Request):
    payload = await request.json()

    print("\nTEST RECEIVER")
    print("Received payload:")
    print(payload)

    return {
        "status": "received",
        "message": "Test receiver accepted webhook",
    }


@router.post("/fail")
async def fail_receiver(request: Request):
    payload = await request.json()

    print("\nTEST RECEIVER - FAILURE MODE")
    print("Received payload:")
    print(payload)

    return JSONResponse(
        status_code=500,
        content={
            "status": "failed",
            "message": "Test receiver intentionally returned failure",
        },
    )

recovery_attempts = {}


@router.post("/recover")
async def recover_receiver(request: Request):
    payload = await request.json()

    event_id = request.headers.get("X-WebhookPulse-Event-ID")

    if not event_id:
        return JSONResponse(
            status_code=400,
            content={
                "status": "failed",
                "message": "Missing X-WebhookPulse-Event-ID",
            },
        )

    recovery_attempts[event_id] = (
        recovery_attempts.get(event_id, 0) + 1
    )

    attempt_number = recovery_attempts[event_id]

    print("\nTEST RECEIVER - RECOVERY MODE")
    print(f"Event ID: {event_id}")
    print(f"Receiver attempt: {attempt_number}")
    print(f"Payload: {payload}")

    if attempt_number < 3:
        return JSONResponse(
            status_code=500,
            content={
                "status": "failed",
                "message": (
                    f"Intentional failure "
                    f"#{attempt_number}"
                ),
            },
        )

    return {
        "status": "received",
        "message": "Test receiver recovered successfully",
        "attempt": attempt_number,
    }
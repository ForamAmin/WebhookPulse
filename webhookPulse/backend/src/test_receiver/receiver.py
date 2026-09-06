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
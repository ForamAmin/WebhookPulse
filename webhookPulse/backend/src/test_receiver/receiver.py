from fastapi import APIRouter, Request


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
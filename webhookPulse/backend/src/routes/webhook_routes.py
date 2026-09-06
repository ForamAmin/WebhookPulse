from fastapi import APIRouter, Request

from src.controllers.webhook_controller import (
    receive_webhook,
)


router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


@router.post("/{endpoint_id}")
async def webhook(
    endpoint_id: str,
    request: Request,
):

    raw_body = await request.body()

    headers = dict(request.headers)

    event = await receive_webhook(
        endpoint_id=endpoint_id,
        raw_body=raw_body,
        headers=headers,
    )

    return {
        "message": "webhook received",
        "event_id": event["event_id"],
        "correlation_id": event["correlation_id"],
    }
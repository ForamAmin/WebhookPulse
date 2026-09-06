from fastapi import APIRouter, Depends
from pydantic import BaseModel, HttpUrl

from src.controllers.endpoint_controller import (
    create_endpoint,
    list_endpoints,
)
from src.core.dependencies import get_current_user


router = APIRouter(
    prefix="/endpoints",
    tags=["Webhook Endpoints"],
)


class CreateEndpointRequest(BaseModel):
    provider: str
    destination_url: HttpUrl
    signing_secret: str


@router.post("")
def create_endpoint_route(
    data: CreateEndpointRequest,
    current_user: dict = Depends(get_current_user),
):
    endpoint = create_endpoint(
        tenant_id=current_user["tenant_id"],
        provider=data.provider,
        destination_url=str(data.destination_url),
        signing_secret=data.signing_secret,
    )

    return {
        "endpoint_id": endpoint["endpoint_id"],
        "provider": endpoint["provider"],
        "destination_url": endpoint["destination_url"],
        "webhook_url": (
            f"http://127.0.0.1:8000/"
            f"webhooks/{endpoint['endpoint_id']}"
        ),
        "status": endpoint["status"],
        "created_at": endpoint["created_at"],
    }


@router.get("")
def list_endpoint_route(
    current_user: dict = Depends(get_current_user),
):
    endpoints = list_endpoints(
        tenant_id=current_user["tenant_id"]
    )

    return [
        {
            "endpoint_id": endpoint["endpoint_id"],
            "provider": endpoint["provider"],
            "destination_url": endpoint["destination_url"],
            "status": endpoint["status"],
            "created_at": endpoint["created_at"],
        }
        for endpoint in endpoints
    ]
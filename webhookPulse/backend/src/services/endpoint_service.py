import secrets

from fastapi import HTTPException, status

from src.models.webhook_endpoint import (
    create_webhook_endpoint_document,
)
from src.repositories.endpoint_repository import (
    create_endpoint,
    get_endpoints_by_tenant,
)


def generate_endpoint_id() -> str:
    return f"ep_{secrets.token_urlsafe(16)}"


def create_endpoint_for_tenant(
    tenant_id: str,
    provider: str,
    destination_url: str,
    signing_secret: str,
):

    endpoint_id = generate_endpoint_id()

    document = create_webhook_endpoint_document(
        tenant_id=tenant_id,
        provider=provider,
        destination_url=destination_url,
        signing_secret=signing_secret,
        endpoint_id=endpoint_id,
    )

    create_endpoint(document)

    return document


def list_endpoints_for_tenant(tenant_id: str):
    return get_endpoints_by_tenant(tenant_id)
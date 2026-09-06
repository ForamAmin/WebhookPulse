import json
import secrets

from fastapi import HTTPException, status

from src.models.event import create_event_document
from src.repositories.endpoint_repository import (
    get_endpoint_by_id,
)
from src.repositories.event_repository import create_event
from src.providers import provider_registry


def ingest_webhook(
    endpoint_id: str,
    raw_body: bytes,
    headers: dict,
):

    endpoint = get_endpoint_by_id(endpoint_id)

    if not endpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found",
        )

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    provider = endpoint["provider"]

    try:
        adapter = provider_registry.get(provider)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported provider: {provider}",
        )

    if not adapter.verify_signature(
        raw_body,
        headers,
        endpoint["signing_secret"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    normalized_event = adapter.normalize_event(
        raw_body,
        headers,
        payload,
    )

    event_id = f"evt_{secrets.token_urlsafe(16)}"
    correlation_id = f"corr_{secrets.token_urlsafe(16)}"

    event_document = create_event_document(
        event_id=event_id,
        tenant_id=endpoint["tenant_id"],
        endpoint_id=endpoint["endpoint_id"],
        provider=provider,
        provider_event_id=normalized_event[
            "provider_event_id"
        ],
        event_type=normalized_event[
            "event_type"
        ],
        correlation_id=correlation_id,
        payload=normalized_event["payload"],
    )

    create_event(event_document)

    return event_document
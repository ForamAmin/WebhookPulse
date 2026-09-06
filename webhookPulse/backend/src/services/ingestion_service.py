import hashlib
import json
import secrets

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from src.models.event import create_event_document
from src.repositories.endpoint_repository import get_endpoint_by_id
from src.repositories.event_repository import (
    create_event,
    get_event_by_dedupe_key,
)
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

    # 1. Verify provider signature
    if not adapter.verify_signature(
        raw_body,
        headers,
        endpoint["signing_secret"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )

    # 2. Normalize provider-specific event
    normalized_event = adapter.normalize_event(
        raw_body,
        headers,
        payload,
    )

    provider_event_id = normalized_event["provider_event_id"]

    # 3. Generate deterministic dedupe key
    if provider_event_id:
        dedupe_key = provider_event_id
    else:
        dedupe_key = hashlib.sha256(raw_body).hexdigest()

    # 4. Check whether we've already received this event
    existing_event = get_event_by_dedupe_key(
        endpoint_id=endpoint_id,
        dedupe_key=dedupe_key,
    )

    if existing_event:
        return {
            "event": existing_event,
            "duplicate": True,
        }

    # 5. Create new internal event
    event_id = f"evt_{secrets.token_urlsafe(16)}"
    correlation_id = f"corr_{secrets.token_urlsafe(16)}"

    event_document = create_event_document(
        event_id=event_id,
        tenant_id=endpoint["tenant_id"],
        endpoint_id=endpoint["endpoint_id"],
        provider=provider,
        provider_event_id=provider_event_id,
        dedupe_key=dedupe_key,
        event_type=normalized_event["event_type"],
        correlation_id=correlation_id,
        payload=normalized_event["payload"],
    )

    # 6. Database uniqueness protects against race conditions
    try:
        create_event(event_document)
    except DuplicateKeyError:
        existing_event = get_event_by_dedupe_key(
            endpoint_id=endpoint_id,
            dedupe_key=dedupe_key,
        )

        return {
            "event": existing_event,
            "duplicate": True,
        }

    return {
        "event": event_document,
        "duplicate": False,
    }
from datetime import datetime, timezone


def create_webhook_endpoint_document(
    tenant_id: str,
    provider: str,
    destination_url: str,
    signing_secret: str,
    endpoint_id: str,
) -> dict:
    return {
        "endpoint_id": endpoint_id,
        "tenant_id": tenant_id,
        "provider": provider,
        "destination_url": destination_url,
        "signing_secret": signing_secret,
        "status": "active",
        "created_at": datetime.now(timezone.utc),
    }
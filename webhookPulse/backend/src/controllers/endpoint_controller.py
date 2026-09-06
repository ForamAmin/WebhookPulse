from src.services.endpoint_service import (
    create_endpoint_for_tenant,
    list_endpoints_for_tenant,
)


def create_endpoint(
    tenant_id: str,
    provider: str,
    destination_url: str,
    signing_secret: str,
):
    return create_endpoint_for_tenant(
        tenant_id=tenant_id,
        provider=provider,
        destination_url=destination_url,
        signing_secret=signing_secret,
    )


def list_endpoints(tenant_id: str):
    return list_endpoints_for_tenant(tenant_id)
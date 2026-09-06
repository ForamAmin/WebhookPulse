from src.infrastructure.database import webhook_endpoints_collection


def create_endpoint(document: dict):
    webhook_endpoints_collection.insert_one(document)
    return document


def get_endpoint_by_id(endpoint_id: str):
    return webhook_endpoints_collection.find_one(
        {"endpoint_id": endpoint_id}
    )


def get_endpoints_by_tenant(tenant_id: str):
    return list(
        webhook_endpoints_collection.find(
            {"tenant_id": tenant_id}
        )
    )


def get_endpoint_by_id_and_tenant(
    endpoint_id: str,
    tenant_id: str,
):
    return webhook_endpoints_collection.find_one(
        {
            "endpoint_id": endpoint_id,
            "tenant_id": tenant_id,
        }
    )
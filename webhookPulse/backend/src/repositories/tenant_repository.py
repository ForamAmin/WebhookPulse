from bson import ObjectId

from src.infrastructure.database import tenants_collection


def create_tenant(document: dict):
    result = tenants_collection.insert_one(document)
    return str(result.inserted_id)


def get_tenant_by_id(tenant_id: str):
    try:
        return tenants_collection.find_one(
            {"_id": ObjectId(tenant_id)}
        )
    except Exception:
        return None
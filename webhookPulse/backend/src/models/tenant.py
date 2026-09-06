from datetime import datetime, timezone


def create_tenant_document(name: str) -> dict:
    return {
        "name": name,
        "created_at": datetime.now(timezone.utc),
    }
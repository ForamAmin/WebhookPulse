from datetime import datetime, timezone


def create_user_document(
    email: str,
    password_hash: str,
    tenant_id: str,
    role: str = "admin",
) -> dict:
    return {
        "email": email,
        "password_hash": password_hash,
        "tenant_id": tenant_id,
        "role": role,
        "created_at": datetime.now(timezone.utc),
    }
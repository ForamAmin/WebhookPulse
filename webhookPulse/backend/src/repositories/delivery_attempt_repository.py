from src.infrastructure.database import delivery_attempts_collection


def create_delivery_attempt(document: dict):
    delivery_attempts_collection.insert_one(document)
    return document


def get_attempts_for_event(
    event_id: str,
    tenant_id: str,
):
    return list(
        delivery_attempts_collection.find(
            {
                "event_id": event_id,
                "tenant_id": tenant_id,
            }
        ).sort("attempt_number", 1)
    )
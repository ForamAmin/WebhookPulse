from src.infrastructure.database import events_collection


def create_event(document: dict):
    events_collection.insert_one(document)
    return document


def get_event_by_id(
    event_id: str,
    tenant_id: str,
):
    return events_collection.find_one(
        {
            "event_id": event_id,
            "tenant_id": tenant_id,
        }
    )
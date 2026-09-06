from src.infrastructure.database import events_collection


def create_event(document: dict):
    events_collection.insert_one(document)
    return document


def get_event_by_id(event_id: str, tenant_id: str):
    return events_collection.find_one(
        {
            "event_id": event_id,
            "tenant_id": tenant_id,
        }
    )


def get_event_by_dedupe_key(
    endpoint_id: str,
    dedupe_key: str,
):
    return events_collection.find_one(
        {
            "endpoint_id": endpoint_id,
            "dedupe_key": dedupe_key,
        }
    )

def update_event_status(
    event_id: str,
    tenant_id: str,
    status: str,
    attempt_count: int,
):
    return events_collection.update_one(
        {
            "event_id": event_id,
            "tenant_id": tenant_id,
        },
        {
            "$set": {
                "status": status,
                "attempt_count": attempt_count,
            }
        },
    )
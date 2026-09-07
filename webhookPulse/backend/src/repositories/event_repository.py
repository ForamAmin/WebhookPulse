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

def get_event_details(
    event_id: str,
    tenant_id: str,
):
    return events_collection.find_one(
        {
            "event_id": event_id,
            "tenant_id": tenant_id,
        }
    )

def get_events_by_tenant(tenant_id: str):
    return list(
        events_collection.find(
            {
                "tenant_id": tenant_id,
            }
        ).sort("created_at", -1)
    )

def get_event_stats_by_tenant(tenant_id: str):
    pipeline = [
        {
            "$match": {
                "tenant_id": tenant_id,
            }
        },
        {
            "$group": {
                "_id": "$status",
                "count": {
                    "$sum": 1
                },
            }
        },
    ]

    results = list(
        events_collection.aggregate(pipeline)
    )

    stats = {
        "total": 0,
        "delivered": 0,
        "processing": 0,
        "retrying": 0,
        "dlq": 0,
        "received": 0,
        "queued": 0,
    }

    for result in results:
        event_status = result["_id"]
        count = result["count"]

        if event_status in stats:
            stats[event_status] = count

        stats["total"] += count

    return stats
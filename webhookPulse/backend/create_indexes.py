from src.infrastructure.database import events_collection


result = events_collection.create_index(
    [
        ("endpoint_id", 1),
        ("dedupe_key", 1),
    ],
    unique=True,
)

print("Created index:", result)
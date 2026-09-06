from src.services.ingestion_service import ingest_webhook


async def receive_webhook(
    endpoint_id: str,
    raw_body: bytes,
    headers: dict,
):
    return ingest_webhook(
        endpoint_id=endpoint_id,
        raw_body=raw_body,
        headers=headers,
    )
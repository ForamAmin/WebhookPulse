from src.services.queue_service import enqueue_event


test_event = {
    "event_id": "evt_queue_test_001",
    "tenant_id": "tenant_test_001",
    "endpoint_id": "ep_test_001",
    "correlation_id": "corr_queue_test_001",
}

message_id = enqueue_event(test_event)

print("Redis message ID:", message_id)
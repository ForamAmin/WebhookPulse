import redis

from src.core.config import REDIS_URL


redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)


WEBHOOK_STREAM = "webhookpulse:events"
DLQ_STREAM = "webhookpulse:dlq"
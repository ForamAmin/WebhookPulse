from src.infrastructure.database import client, db
from src.infrastructure.redis import redis_client


print("Testing MongoDB...")

try:
    client.admin.command("ping")
    print("MongoDB: CONNECTED")
    print("Database:", db.name)
except Exception as e:
    print("MongoDB: FAILED")
    print(e)


print("\nTesting Redis...")

try:
    redis_client.ping()
    print("Redis: CONNECTED")
except Exception as e:
    print("Redis: FAILED")
    print(e)
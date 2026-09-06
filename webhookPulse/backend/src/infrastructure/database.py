from pymongo import MongoClient

from src.core.config import MONGO_DATABASE, MONGO_URI


client = MongoClient(MONGO_URI)

db = client[MONGO_DATABASE]


tenants_collection = db["tenants"]
users_collection = db["users"]
webhook_endpoints_collection = db["webhook_endpoints"]
events_collection = db["events"]
delivery_attempts_collection = db["delivery_attempts"]
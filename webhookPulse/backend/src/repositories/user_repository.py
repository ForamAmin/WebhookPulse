from bson import ObjectId

from src.infrastructure.database import users_collection


def create_user(document: dict):
    result = users_collection.insert_one(document)
    return str(result.inserted_id)


def get_user_by_email(email: str):
    return users_collection.find_one({"email": email})


def get_user_by_id(user_id: str):
    try:
        return users_collection.find_one(
            {"_id": ObjectId(user_id)}
        )
    except Exception:
        return None
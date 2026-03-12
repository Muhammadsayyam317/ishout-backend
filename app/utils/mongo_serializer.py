from bson import ObjectId
from datetime import datetime


def serialize_mongo_data(data):
    """
    Recursively converts:
    - ObjectId -> str
    - datetime -> isoformat string
    """

    if isinstance(data, list):
        return [serialize_mongo_data(item) for item in data]

    if isinstance(data, dict):
        return {
            key: serialize_mongo_data(value)
            for key, value in data.items()
        }

    if isinstance(data, ObjectId):
        return str(data)

    if isinstance(data, datetime):
        return data.isoformat()

    return data
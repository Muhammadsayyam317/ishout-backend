from typing import Any, Dict
from app.db.connection import get_db
from app.utils.printcolors import Colors
from app.core.exception import InternalServerErrorException
from app.utils.mongo_serializer import serialize_mongo_data
from bson import ObjectId


async def get_all_negotiation_controls(
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:
    try:
        db = get_db()
        collection = db.get_collection("negotiation_agent_controls")
        skip = (page - 1) * page_size

        total_count = await collection.count_documents({})
        negotiation_controls = (
            await collection.find({})
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
            .to_list(length=None)
        )

        # Serialize Mongo data
        negotiation_controls_serialized = serialize_mongo_data(negotiation_controls)

        total_pages = (total_count + page_size - 1) // page_size
        return {
            "negotiation_controls": negotiation_controls_serialized,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    except Exception as e:
        print(f"{Colors.RED}Error in negotiationstats: {e}")
        print("--------------------------------")
        raise InternalServerErrorException(
            message=f"Error in negotiationstats: {str(e)}"
        ) from e


async def get_negotiation_control_detail(_id: str) -> Dict[str, Any]:
    try:
        db = get_db()
        collection = db.get_collection("negotiation_agent_controls")
        try:
            object_id = ObjectId(_id)
        except Exception:
            return None  

        document = await collection.find_one({"_id": object_id})
        if not document:
            return None

        serialized_doc = serialize_mongo_data(document)

        return {
            "name": serialized_doc.get("name"),
            "phone": serialized_doc.get("sender_id"),
            "history": serialized_doc.get("history", []),
            "conversation_mode": serialized_doc.get("conversation_mode"),
        }

    except Exception as e:
        print(f"{Colors.RED}Error in get_negotiation_control_detail: {e}")
        raise InternalServerErrorException(
            message=f"Error in get_negotiation_control_detail: {str(e)}"
        ) from e

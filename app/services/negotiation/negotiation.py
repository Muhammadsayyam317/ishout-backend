from typing import Any, Dict
from app.db.connection import get_db
from app.utils.printcolors import Colors
from app.core.exception import InternalServerErrorException


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
        total_pages = (total_count + page_size - 1) // page_size
        return {
            "negotiation_controls": negotiation_controls,
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

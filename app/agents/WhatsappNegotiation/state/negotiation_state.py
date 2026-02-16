from datetime import datetime, timezone
from app.db.connection import get_db
from typing import Optional
from app.utils.printcolors import Colors
from app.core.exception import InternalServerErrorException


async def update_negotiation_state(thread_id: str, data: dict) -> Optional[dict]:
    print(f"{Colors.GREEN}Entering into update_negotiation_state")
    print("--------------------------------")
    try:
        db = get_db()
        collection = db.get_collection("negotiation_agent_controls")
        data["_updated_at"] = datetime.now(timezone.utc)
        await collection.update_one(
            {"thread_id": thread_id},
            {"$set": data},
            upsert=True,
        )
        updated_doc = await collection.find_one({"thread_id": thread_id})
        print(f"{Colors.CYAN}Updated negotiation state: {updated_doc}")
        print("--------------------------------")
        print(f"{Colors.YELLOW} Exiting from update_negotiation_state")
        print("--------------------------------")
        return updated_doc
    except Exception as e:
        print(f"{Colors.RED}[update_negotiation_state] Failed for {thread_id}: {e}")
        print("--------------------------------")
        raise InternalServerErrorException(
            message=f"Error in update_negotiation_state: {str(e)}"
        ) from e


async def get_negotiation_state(thread_id: str) -> Optional[dict]:
    print(f"{Colors.GREEN}Entering into get_negotiation_state")
    print("--------------------------------")
    try:
        db = get_db()
        collection = db.get_collection("negotiation_agent_controls")
        doc = await collection.find_one({"thread_id": thread_id})
        print(f"{Colors.CYAN}Negotiation state: {doc}")
        print("--------------------------------")
        print(f"{Colors.YELLOW} Exiting from get_negotiation_state")
        print("--------------------------------")
        return doc
    except Exception as e:
        print(f"{Colors.RED}[get_negotiation_state] Failed for {thread_id}: {e}")
        print("--------------------------------")
        raise InternalServerErrorException(
            message=f"Error in get_negotiation_state: {str(e)}"
        ) from e

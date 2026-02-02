from typing import Any, Dict
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db


async def agent_control_info(
    thread_id: str,
) -> Dict[str, Any]:
    try:
        db = get_db()
        Whatsapp_agentcontrol = db.get_collection("agent_controls")
        result = await Whatsapp_agentcontrol.find_one({"thread_id": thread_id})
        if not result:
            return {"message": "Whatsapp agent control not found", "data": None}
        return {
            "agent_paused": result.get("agent_paused"),
            "human_takeover": result.get("human_takeover"),
        }
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in get whatsapp agent control: {str(e)}"
        ) from e

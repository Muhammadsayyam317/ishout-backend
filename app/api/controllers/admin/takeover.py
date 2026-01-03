from datetime import datetime, timezone
from fastapi import APIRouter
from app.db.connection import get_db
from app.services.whatsapp.save_message import save_conversation_message
from app.services.whatsapp.send_text import send_whatsapp_text_message
from app.core.exception import InternalServerErrorException

router = APIRouter()


async def human_takeover(thread_id: str):
    db = get_db()
    await db.get_collection("agent_controls").update_one(
        {"thread_id": thread_id},
        {
            "$set": {
                "human_takeover": True,
                "agent_paused": True,
                "updated_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )
    return {"success": True, "mode": "HUMAN_TAKEOVER"}


async def pause_agent(thread_id: str):
    db = get_db()
    await db.get_collection("agent_controls").update_one(
        {"thread_id": thread_id},
        {
            "$set": {
                "agent_paused": True,
                "human_takeover": False,
                "updated_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )
    return {"success": True, "mode": "AGENT_PAUSED"}


async def resume_agent(thread_id: str):
    db = get_db()
    await db.get_collection("agent_controls").update_one(
        {"thread_id": thread_id},
        {
            "$set": {
                "agent_paused": False,
                "human_takeover": False,
                "updated_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )
    return {"success": True, "mode": "AI_ACTIVE"}


async def send_human_message(
    thread_id: str,
    message: str,
    admin_name: str = "Admin",
):
    try:
        db = get_db()
        control = await db.get_collection("agent_controls").find_one(
            {"thread_id": thread_id}
        )

        if not control or not control.get("human_takeover"):
            raise InternalServerErrorException(
                message="Human takeover is not active for this chat"
            )
        await send_whatsapp_text_message(to=thread_id, text=message)
        await save_conversation_message(
            thread_id=thread_id,
            sender="HUMAN",
            username=admin_name,
            message=message,
            agent_paused=True,
            human_takeover=True,
        )
        return {"success": True, "message": "Message sent successfully"}
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e

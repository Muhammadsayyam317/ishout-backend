from datetime import datetime, timezone
from fastapi import APIRouter
from app.db.connection import get_db
from app.services.whatsapp.save_message import save_conversation_message
from app.services.whatsapp.send_text import send_whatsapp_text_message
from app.core.exception import InternalServerErrorException

router = APIRouter()


async def toggle_human_takeover(thread_id: str, enabled: bool):
    try:
        db = get_db()
        controls = db.get_collection("agent_controls")
        if enabled:
            # 🔴 SWITCH ON → Human takeover
            await controls.update_one(
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

            system_message = (
                "👤 *Human takeover enabled*\n\n"
                "A human agent has joined the conversation."
            )
            await send_whatsapp_text_message(to=thread_id, text=system_message)
            await save_conversation_message(
                thread_id=thread_id,
                sender="SYSTEM",
                message=system_message,
                agent_paused=True,
                human_takeover=True,
            )
            return {
                "success": True,
                "mode": "HUMAN_TAKEOVER",
                "message": "Human takeover enabled",
            }
        else:
            # 🟢 SWITCH OFF → Resume AI
            await controls.update_one(
                {"thread_id": thread_id},
                {
                    "$set": {
                        "human_takeover": False,
                        "agent_paused": False,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
                upsert=True,
            )
            system_message = (
                "🤖 *AI agent resumed*\n\n"
                "The assistant is now handling the conversation again."
            )
            await send_whatsapp_text_message(to=thread_id, text=system_message)
            await save_conversation_message(
                thread_id=thread_id,
                sender="SYSTEM",
                message=system_message,
                agent_paused=False,
                human_takeover=False,
            )

            return {
                "success": True,
                "mode": "AI_ACTIVE",
                "message": "AI agent resumed",
            }
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


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

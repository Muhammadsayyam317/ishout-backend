from datetime import datetime, timezone
from fastapi import APIRouter
from app.db.connection import get_db
from app.model.Whatsapp_Users_Sessions import HumanMessageRequest
from app.model.takeover import HumanTakeoverRequest
from app.services.websocket_manager import ws_manager
from app.services.whatsapp.save_message import save_conversation_message
from app.services.whatsapp.save_negotiation_message import save_negotiation_message
from app.services.whatsapp.send_text import send_whatsapp_text_message
from app.core.exception import InternalServerErrorException
from app.config.credentials_config import config
from app.agents.WhatsappNegotiation.state.negotiation_state import (
    get_negotiation_state,
    update_negotiation_state,
)

router = APIRouter()


async def toggle_human_takeover(thread_id: str, payload: HumanTakeoverRequest):
    enabled: bool = payload.enabled
    try:
        db = get_db()
        controls = db.get_collection(config.MONGODB_AGENT_CONTROL)
        existing = await controls.find_one({"thread_id": thread_id})
        current_state = existing.get("human_takeover") if existing else False
        if enabled == current_state:
            return {
                "success": True,
                "message": "No state change",
                "mode": "HUMAN_TAKEOVER" if enabled else "AI_ACTIVE",
            }
        if enabled:
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
                "A human from ishout is now handling this conversation."
            )
            await send_whatsapp_text_message(to=thread_id, text=system_message)
            await save_conversation_message(
                thread_id=thread_id,
                sender="SYSTEM",
                message=system_message,
                agent_paused=True,
                human_takeover=True,
            )
            await ws_manager.broadcast_event(
                event_type="CONTROL_UPDATE",
                payload={
                    "thread_id": thread_id,
                    "human_takeover": True,
                    "agent_paused": True,
                },
            )
            await ws_manager.broadcast_event(
                event_type="whatsapp.message",
                payload={
                    "thread_id": thread_id,
                    "sender": "SYSTEM",
                    "message": system_message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
            return {
                "success": True,
                "mode": "HUMAN_TAKEOVER",
                "message": "Human takeover enabled",
            }
        else:
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
                "The ishout agent is now handling this conversation again."
            )
            await send_whatsapp_text_message(to=thread_id, text=system_message)
            await save_conversation_message(
                thread_id=thread_id,
                sender="SYSTEM",
                message=system_message,
                agent_paused=False,
                human_takeover=False,
            )
            await ws_manager.broadcast_event(
                event_type="CONTROL_UPDATE",
                payload={
                    "thread_id": thread_id,
                    "human_takeover": False,
                    "agent_paused": False,
                },
            )
            await ws_manager.broadcast_event(
                event_type="whatsapp.message",
                payload={
                    "thread_id": thread_id,
                    "sender": "SYSTEM",
                    "message": system_message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
            return {
                "success": True,
                "mode": "AI_ACTIVE",
                "message": "AI agent resumed",
            }
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


async def takeover_value(thread_id: str):
    try:
        db = get_db()
        control = await db.get_collection(config.MONGODB_AGENT_CONTROL).find_one(
            {"thread_id": thread_id}
        )
        if control:
            return {
                "success": True,
                "mode": (
                    "HUMAN_TAKEOVER" if control.get("human_takeover") else "AI_ACTIVE"
                ),
            }
        else:
            return {
                "success": False,
                "message": "No control found",
            }
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


async def send_human_message(thread_id: str, payload: HumanMessageRequest):
    try:
        db = get_db()
        control = await db.get_collection(config.MONGODB_AGENT_CONTROL).find_one(
            {"thread_id": thread_id}
        )
        if not control or not control.get("human_takeover"):
            raise InternalServerErrorException(
                message="ADMIN takeover is not active for this chat"
            )
        await send_whatsapp_text_message(to=thread_id, text=payload.message)
        await save_conversation_message(
            thread_id=thread_id,
            sender="ADMIN",
            message=payload.message,
            agent_paused=True,
            human_takeover=True,
        )
        await ws_manager.broadcast_event(
            event_type="whatsapp.message",
            payload={
                "thread_id": thread_id,
                "sender": "ADMIN",
                "message": payload.message,
                "timestamp": datetime.now(timezone.utc),
            },
        )
        print("ws_manager.broadcast_event payload", payload)
        return {"success": True, "message": "Message sent successfully"}
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


async def toggle_negotiation_takeover(thread_id: str, payload: HumanTakeoverRequest):
    enabled: bool = payload.enabled
    try:
        negotiation_state = await get_negotiation_state(thread_id)
        if not negotiation_state:
            raise InternalServerErrorException(
                message="No negotiation state found for this thread"
            )

        current_state = negotiation_state.get("human_takeover", False)
        if enabled == current_state:
            return {
                "success": True,
                "message": "No state change",
                "mode": "HUMAN_TAKEOVER" if enabled else "AI_ACTIVE",
            }

        if enabled:
            await update_negotiation_state(
                thread_id,
                {
                    "human_takeover": True,
                    "agent_paused": True,
                    "admin_takeover": True,
                    "conversation_mode": "NEGOTIATION",
                    "negotiation_status": "manual_required",
                    "next_action": None,
                },
            )
            system_message = (
                "👤 *Human takeover enabled*\n\n"
                "A human from ishout is now handling this negotiation."
            )
            await send_whatsapp_text_message(to=thread_id, text=system_message)
            await save_negotiation_message(
                thread_id=thread_id,
                sender="SYSTEM",
                message=system_message,
                agent_paused=True,
                human_takeover=True,
            )
            await ws_manager.broadcast_event(
                event_type="NEGOTIATION_CONTROL_UPDATE",
                payload={
                    "thread_id": thread_id,
                    "human_takeover": True,
                    "agent_paused": True,
                },
            )
            await ws_manager.broadcast_event(
                event_type="whatsapp.message",
                payload={
                    "thread_id": thread_id,
                    "sender": "SYSTEM",
                    "message": system_message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
            return {
                "success": True,
                "mode": "HUMAN_TAKEOVER",
                "message": "Human takeover enabled for negotiation",
            }
        else:
            await update_negotiation_state(
                thread_id,
                {
                    "human_takeover": False,
                    "agent_paused": False,
                    "admin_takeover": False,
                    "conversation_mode": "NEGOTIATION",
                },
            )
            system_message = (
                "🤖 *AI agent resumed*\n\n"
                "The ishout negotiation agent is now handling this conversation again."
            )
            await send_whatsapp_text_message(to=thread_id, text=system_message)
            await save_negotiation_message(
                thread_id=thread_id,
                sender="SYSTEM",
                message=system_message,
                agent_paused=False,
                human_takeover=False,
            )
            await ws_manager.broadcast_event(
                event_type="NEGOTIATION_CONTROL_UPDATE",
                payload={
                    "thread_id": thread_id,
                    "human_takeover": False,
                    "agent_paused": False,
                },
            )
            await ws_manager.broadcast_event(
                event_type="whatsapp.message",
                payload={
                    "thread_id": thread_id,
                    "sender": "SYSTEM",
                    "message": system_message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
            return {
                "success": True,
                "mode": "AI_ACTIVE",
                "message": "AI negotiation agent resumed",
            }
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


async def negotiation_takeover_value(thread_id: str):
    try:
        negotiation_state = await get_negotiation_state(thread_id)
        if negotiation_state:
            return {
                "success": True,
                "mode": (
                    "HUMAN_TAKEOVER"
                    if negotiation_state.get("human_takeover")
                    else "AI_ACTIVE"
                ),
            }
        else:
            return {
                "success": False,
                "message": "No negotiation state found",
            }
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


async def send_negotiation_human_message(thread_id: str, payload: HumanMessageRequest):
    try:
        negotiation_state = await get_negotiation_state(thread_id)
        if not negotiation_state or not negotiation_state.get("human_takeover"):
            raise InternalServerErrorException(
                message="ADMIN takeover is not active for this negotiation"
            )
        await send_whatsapp_text_message(to=thread_id, text=payload.message)
        await save_negotiation_message(
            thread_id=thread_id,
            sender="ADMIN",
            message=payload.message,
            agent_paused=True,
            human_takeover=True,
        )
        await ws_manager.broadcast_event(
            event_type="whatsapp.message",
            payload={
                "thread_id": thread_id,
                "sender": "ADMIN",
                "message": payload.message,
                "timestamp": datetime.now(timezone.utc),
            },
        )
        return {"success": True, "message": "Message sent successfully"}
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e

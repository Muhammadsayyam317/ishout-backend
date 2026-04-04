from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.db.connection import get_db
from app.model.Whatsapp_Users_Sessions import (
    HumanMessageRequest,
    AdminApproveVideoRequest,
)
from app.model.takeover import HumanTakeoverRequest, NegotiationApprovalRequest
from app.services.websocket_manager import ws_manager
from app.services.whatsapp.save_message import save_conversation_message
from app.services.whatsapp.save_negotiation_message import save_negotiation_message
from app.services.whatsapp.save_admin_influencer_message import (
    save_admin_influencer_message,
)
from app.services.whatsapp.save_admin_company_message import (
    save_admin_company_message,
)
from app.services.whatsapp.send_text import send_whatsapp_text_message
from app.core.exception import InternalServerErrorException
from app.config.credentials_config import config
from bson import ObjectId
from app.agents.WhatsappNegotiation.state.negotiation_state import (
    get_negotiation_state,
    update_negotiation_state,
)
from app.utils.helpers import normalize_phone

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


async def send_admin_influencer_message(
    thread_id: str,
    payload: HumanMessageRequest,
):
    """
    Admin sends a human message to influencer (admin<->influencer flow).
    Persist into `whatsapp_admin_influencer` collection.
    """
    try:
        await send_whatsapp_text_message(to=thread_id, text=payload.message)
        await save_admin_influencer_message(
            thread_id=thread_id,
            username="ADMIN",
            sender="ADMIN",
            message=payload.message,
            agent_paused=True,
            human_takeover=True,
        )
        return {"success": True, "message": "Message sent successfully"}
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


async def send_admin_company_message(
    thread_id: str,
    payload: HumanMessageRequest,
):
    """
    Admin dashboard → company: persist only (no outbound WhatsApp).
    Stored in `whatsapp_admin_company` collection.
    """
    try:
        neg_id = (payload.negotiation_id or "").strip() or None
        await save_admin_company_message(
            thread_id=thread_id,
            username="ADMIN",
            sender="ADMIN",
            message=payload.message,
            agent_paused=True,
            human_takeover=True,
            negotiation_id=neg_id,
        )
        return {"success": True, "message": "Message sent successfully"}
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


async def send_company_admin_message(user_id: str, payload: HumanMessageRequest):
    """
    Company dashboard sends a message to admin dashboard.

    Dashboard-only: do NOT send WhatsApp.
    Persist into `whatsapp_admin_company` collection with `conversation_mode="Company_Admin"`.
    """
    try:
        db = get_db()
        users_collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_USERS)
        user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise InternalServerErrorException(message="Company user not found")

        phone = user_doc.get("phone")
        company_name = user_doc.get("company_name")

        thread_id = normalize_phone(phone) if phone is not None else None
        if not thread_id:
            raise InternalServerErrorException(
                message="Company phone number is missing or invalid"
            )
        if not company_name:
            raise InternalServerErrorException(message="Company name is missing")

        # Sender/username pattern matches WhatsApp inbound routing:
        # - `sender="USER"`
        # - `username` is company's name
        neg_id = (payload.negotiation_id or "").strip() or None
        await save_admin_company_message(
            thread_id=thread_id,
            username=company_name,
            sender="USER",
            message=payload.message,
            agent_paused=True,
            human_takeover=True,
            conversation_mode="Company_Admin",
            negotiation_id=neg_id,
        )

        return {"success": True, "message": "Message sent successfully"}
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


async def admin_approve_video_to_brand(payload: AdminApproveVideoRequest):
    """
    When admin approves influencer video, store it into `whatsapp_admin_company`
    so it appears in the brand chat (filtered by thread_id + negotiation_id).
    Also upsert a row in `MONGODB_APPROVED_CONTENT` for audit / listings.
    """
    try:
        neg_id = (payload.negotiation_id or "").strip()
        campaign_id = (payload.campaign_id or "").strip()
        video_url = (payload.video_url or "").strip()
        brand_thread_id = (payload.brand_thread_id or "").strip()

        if not neg_id or not campaign_id or not video_url or not brand_thread_id:
            raise HTTPException(
                status_code=400,
                detail=(
                    "negotiation_id, campaign_id, video_url, and brand_thread_id "
                    "are required."
                ),
            )

        await save_admin_company_message(
            thread_id=brand_thread_id,
            username="ADMIN",
            sender="ADMIN",
            message=video_url,
            agent_paused=True,
            human_takeover=True,
            conversation_mode="ADMIN_COMPANY_VIDEO",
            negotiation_id=neg_id,
            video_url=video_url,
            video_approve_admin=payload.video_approve_admin,
            video_approve_brand=payload.video_approve_brand,
            brand_thread_id=brand_thread_id,
        )

        db = get_db()
        approved_coll = db.get_collection(config.MONGODB_APPROVED_CONTENT)
        now = datetime.now(timezone.utc)
        approved_set: dict = {
            "video_url": video_url,
            "campaign_id": campaign_id,
            "negotiation_id": neg_id,
            "brand_thread_id": brand_thread_id,
            "updated_at": now,
        }
        admin_st = (
            (payload.video_approve_admin or "").strip()
            if payload.video_approve_admin is not None
            else ""
        )
        brand_st = (
            (payload.video_approve_brand or "").strip()
            if payload.video_approve_brand is not None
            else ""
        )
        if admin_st:
            approved_set["video_approve_admin"] = admin_st
        if brand_st:
            approved_set["video_approve_brand"] = brand_st

        await approved_coll.update_one(
            {
                "negotiation_id": neg_id,
                "campaign_id": campaign_id,
                "video_url": video_url,
            },
            {"$set": approved_set, "$setOnInsert": {"created_at": now}},
            upsert=True,
        )

        return {"success": True, "message": "Video sent to brand chat"}
    except HTTPException:
        raise
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


async def update_negotiation_approval_status(
    thread_id: str, payload: NegotiationApprovalRequest
):
    """
    Update negotiation approval statuses.
    Accepts only one field at a time:
    - `admin_approved`
    - `Brand_approved`
    Each can be a string or null (to clear).
    """
    data = payload.model_dump(exclude_unset=True)
    has_admin = "admin_approved" in data
    has_brand = "Brand_approved" in data

    if not (has_admin or has_brand):
        raise HTTPException(
            status_code=400,
            detail="Provide one of `admin_approved` or `Brand_approved` in the request body.",
        )
    if has_admin and has_brand:
        raise HTTPException(
            status_code=400,
            detail="Provide only one field at a time: `admin_approved` or `Brand_approved`.",
        )

    update_payload: dict = {}
    if has_admin:
        update_payload["admin_approved"] = data.get("admin_approved")
    else:
        update_payload["Brand_approved"] = data.get("Brand_approved")

    updated = await update_negotiation_state(thread_id, update_payload)

    # Notify frontend about control updates.
    if updated:
        await ws_manager.broadcast_event(
            event_type="NEGOTIATION_CONTROL_UPDATE",
            payload={
                "thread_id": thread_id,
                "admin_approved": updated.get("admin_approved"),
                "Brand_approved": updated.get("Brand_approved"),
            },
        )

    return {
        "success": True,
        "message": "Negotiation approval status updated",
        "thread_id": thread_id,
        "admin_approved": updated.get("admin_approved") if updated else None,
        "Brand_approved": updated.get("Brand_approved") if updated else None,
    }


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

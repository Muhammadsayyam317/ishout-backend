from datetime import datetime, timezone
from fastapi import Request, HTTPException

from app.agents.Whatsapp.nodes.state import (
    cleanup_old_checkpoints,
    get_conversation_round,
    increment_conversation_round,
)
from app.agents.Whatsapp.state.get_user_state import get_user_state
from app.agents.Whatsapp.state.update_user_state import update_user_state
from app.agents.Whatsapp.state.reset_state import reset_user_state
from app.agents.WhatsappNegotiation.invoke.negotiation_invoke import Negotiation_invoke
from app.agents.WhatsappNegotiation.state.negotiation_state import (
    get_negotiation_state,
    update_negotiation_state,
)
from app.utils.message_context import get_history_list
from app.services.websocket_manager import ws_manager
from app.services.whatsapp.reply_button import handle_button_reply
from app.services.whatsapp.save_message import save_conversation_message
from app.utils.Enums.user_enum import SenderType
from app.services.whatsapp.save_admin_influencer_message import (
    save_admin_influencer_message,
)
from app.services.whatsapp.save_admin_company_message import (
    save_admin_company_message,
)
from app.utils.whatsapp_media import upload_whatsapp_media_to_s3


def extract_whatsapp_message(event: dict):
    entry = event.get("entry")
    if not entry:
        return None, None, None, None, None

    changes = entry[0].get("changes")
    if not changes:
        return None, None, None, None, None

    value = changes[0].get("value", {})
    messages = value.get("messages")
    if not messages:
        return None, None, None, None, None

    first_message = messages[0]
    thread_id = first_message.get("from")

    # Detect message type
    msg_type = first_message.get("type", "text")
    msg_text = ""
    
    if msg_type == "text":
        msg_text = first_message.get("text", {}).get("body", "")
    elif msg_type in ["image", "audio", "video", "document"]:
        # For media, we might still want to use the caption as msg_text if it exists
        msg_text = first_message.get(msg_type, {}).get("caption", "")

    # For media messages, also try to get the caption as the display text
    if msg_type in MEDIA_TYPES:
        media_block = first_message.get(msg_type, {})
        if not msg_text:
            msg_text = media_block.get("caption", "") or ""

    profile_name = (
        value.get("contacts", [{}])[0].get("profile", {}).get("name") or "iShout"
    )

    return first_message, thread_id, msg_text, profile_name, value


async def _fetch_meta_media_and_upload_to_s3(
    meta_media_id: str,
    media_mime_type: str | None,
    media_filename: str | None,
    thread_id: str,
) -> str | None:
    """
    Download a media file from Meta's Graph API and upload it to S3.
    Returns the permanent S3 URL, or None on failure.
    """
    try:
        headers = {"Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Step 1: Get the download URL from Meta
            meta_url_resp = await client.get(
                f"https://graph.facebook.com/v22.0/{meta_media_id}",
                headers=headers,
            )
            if meta_url_resp.status_code != 200:
                print(f"[_fetch_meta_media] Meta URL fetch failed: {meta_url_resp.text}")
                return None
            download_url = meta_url_resp.json().get("url")
            if not download_url:
                return None

            # Step 2: Download the actual file
            file_resp = await client.get(download_url, headers=headers)
            if file_resp.status_code != 200:
                print(f"[_fetch_meta_media] Media download failed: {file_resp.status_code}")
                return None
            file_bytes = file_resp.content

        # Step 3: Upload to S3
        mime = media_mime_type or "application/octet-stream"
        ext = (mime.split("/")[-1]).split(";")[0] or "bin"
        filename = media_filename or f"media_{uuid.uuid4()}.{ext}"
        s3_url = await upload_file_to_s3_with_prefix(
            prefix_folder="inbound_media",
            object_id=thread_id,
            file_bytes=file_bytes,
            filename=filename,
            content_type=mime,
        )
        return s3_url
    except Exception as e:
        print(f"[_fetch_meta_media] Error: {e}")
        return None


async def process_incoming_message(
    thread_id,
    profile_name,
    msg_text,
    msg_type: str = "text",
    meta_media_id: str | None = None,
    media_mime_type: str | None = None,
    media_filename: str | None = None,
):
    # For media messages: download from Meta, upload to S3, store permanent S3 URL
    media_url: str | None = None
    if msg_type in MEDIA_TYPES and meta_media_id:
        media_url = await _fetch_meta_media_and_upload_to_s3(
            meta_media_id=meta_media_id,
            media_mime_type=media_mime_type,
            media_filename=media_filename,
            thread_id=thread_id,
        )

    # Use media_url as fallback for message text if it's empty (for backward compatibility)
    display_text = msg_text or media_url or ""

    await save_conversation_message(
        thread_id=thread_id,
        username=profile_name,
        sender=SenderType.USER.value,
        message=display_text,
        message_type=msg_type,
        media_url=media_url,
        media_mime_type=media_mime_type,
        media_filename=media_filename,
    )

    await ws_manager.broadcast_event(
        "whatsapp.message",
        {
            "thread_id": thread_id,
            "sender": "USER",
            "message": display_text,
            "message_type": msg_type,
            "media_url": media_url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


async def handle_negotiation_agent(request, thread_id, msg_text, profile_name):
    negotiation_state = await get_negotiation_state(thread_id)

    if not negotiation_state:
        print(f"[handle_negotiation_agent] No negotiation state found for thread {thread_id}")
        return False

    if negotiation_state.get("agent_paused"):
        # When paused, we must still store + broadcast the absorbed USER message
        # into the negotiation control doc history (so frontend timestamps stay correct).
        timestamp = datetime.now(timezone.utc).isoformat()
        history = get_history_list(negotiation_state)
        history.append(
            {
                "sender_type": "USER",
                "message": msg_text,
                "timestamp": timestamp,
            }
        )

        await update_negotiation_state(
            thread_id,
            {
                "user_message": msg_text,
                "thread_id": thread_id,
                "sender_id": thread_id,
                "name": profile_name,
                "history": history,
                # keep the state flags as-is (update_negotiation_state uses $set)
                "agent_paused": negotiation_state.get("agent_paused"),
                "human_takeover": negotiation_state.get("human_takeover", False),
            },
        )

        await ws_manager.broadcast_event(
            "whatsapp.message",
            {
                "thread_id": thread_id,
                "sender": SenderType.USER.value,
                "message": msg_text,
                "timestamp": timestamp,
                "conversation_mode": "NEGOTIATION",
                "agent_paused": True,
                "human_takeover": negotiation_state.get("human_takeover", False),
            },
        )
        return True

    # Maintain a rolling window of recent conversation history (USER + AI).
    # Normalize to list (Mongo may return history as dict or other type).
    history = get_history_list(negotiation_state)
    history.append(
        {
            "sender_type": "USER",
            "message": msg_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    negotiation_state.update(
        {
            "user_message": msg_text,
            "thread_id": thread_id,
            "sender_id": thread_id,
            "name": profile_name,
            "history": history,
        }
    )

    agent = request.app.state.whatsapp_negotiation_agent
    final_state = await Negotiation_invoke(
        agent,
        negotiation_state,
        config={"configurable": {"thread_id": thread_id}},
    )

    if final_state:
        await update_negotiation_state(thread_id, final_state)
    return True


async def handle_default_agent(request, thread_id, msg_text, profile_name, value):
    whatsapp_agent = getattr(request.app.state, "whatsapp_agent", None)
    if not whatsapp_agent:
        raise HTTPException(
            status_code=503,
            detail="WhatsApp agent not initialized",
        )
    stored_state = await get_user_state(thread_id)
    state = stored_state or {}
    conversation_round = await get_conversation_round(thread_id) or 1
    if state.get("done") and state.get("acknowledged"):
        conversation_round = await increment_conversation_round(thread_id)
        if conversation_round > 1:
            await cleanup_old_checkpoints(thread_id, conversation_round)
        state = await reset_user_state(thread_id)
    checkpoint_thread_id = f"{thread_id}-r{conversation_round}"
    state.update(
        {
            "user_message": msg_text,
            "event_data": value,
            "thread_id": thread_id,
            "sender_id": thread_id,
            "name": profile_name or state.get("name"),
        }
    )
    final_state = await whatsapp_agent.ainvoke(
        state,
        config={"configurable": {"thread_id": checkpoint_thread_id}},
    )
    if final_state:
        await update_user_state(thread_id, final_state)


async def handle_whatsapp_events(request: Request):
    try:
        event = await request.json()
        first_message, thread_id, msg_text, profile_name, value = (
            extract_whatsapp_message(event)
        )
        if not first_message or not thread_id:
            return {"status": "ok"}
            
        # Detect and handle media
        msg_type = first_message.get("type", "text")
        mime_type = None
        filename = None
        
        if msg_type in ["image", "audio", "video", "document"]:
            media_data = first_message.get(msg_type, {})
            media_id = media_data.get("id")
            mime_type = media_data.get("mime_type")
            filename = media_data.get("filename")
            
            if media_id:
                s3_url = await upload_whatsapp_media_to_s3(media_id, msg_type, mime_type)
                if s3_url:
                    # Replace msg_text with S3 URL as requested for the 'content' field
                    msg_text = s3_url
                else:
                    # If upload fails, store null or error marker in content
                    msg_text = None
        
        if (
            first_message.get("type") == "interactive"
            and first_message.get("interactive", {}).get("type") == "button_reply"
        ):
            await handle_button_reply(first_message)
            return {"status": "ok"}

        # Admin flow routing first
        admin_influencer_saved = await save_admin_influencer_message(
            thread_id=thread_id,
            username=profile_name,
            sender=SenderType.USER.value,
            message=msg_text,
            create_if_missing=False,
        )
        if admin_influencer_saved:
            return {"status": "ok"}

        admin_company_saved = await save_admin_company_message(
            thread_id=thread_id,
            username=profile_name,
            sender=SenderType.USER.value,
            message=msg_text,
            create_if_missing=False,
        )
        if admin_company_saved:
            return {"status": "ok"}

        # Otherwise: default WhatsApp message persistence + broadcast
        msg_type = first_message.get("type", "text")
        media_block = first_message.get(msg_type, {}) if msg_type != "text" else {}
        await process_incoming_message(
            thread_id,
            profile_name,
            msg_text,
            msg_type=msg_type,
            meta_media_id=media_block.get("id"),
            media_mime_type=media_block.get("mime_type"),
            media_filename=media_block.get("filename"),
        )

        # negotiation agent
        negotiation_handled = await handle_negotiation_agent(
            request, thread_id, msg_text, profile_name
        )
        if negotiation_handled:
            return {"status": "ok"}

        # Otherwise default agent
        await handle_default_agent(request, thread_id, msg_text, profile_name, value)
        return {"status": "ok"}

    except Exception as e:
        # Keep a minimal log so webhook failures are visible
        print(f"[handle_whatsapp_events] Error in handle_whatsapp_events: {e}")

        raise HTTPException(
            status_code=500,
            detail=f"Webhook processing failed: {str(e)}",
        ) from e

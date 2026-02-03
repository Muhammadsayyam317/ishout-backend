from fastapi import Request, HTTPException
from datetime import datetime, timezone

from app.agents.Whatsapp.nodes.state import (
    cleanup_old_checkpoints,
    get_conversation_round,
    increment_conversation_round,
)
from app.agents.Whatsapp.state.get_user_state import get_user_state
from app.agents.Whatsapp.state.update_user_state import update_user_state
from app.agents.Whatsapp.state.reset_state import reset_user_state
from app.services.websocket_manager import ws_manager
from app.services.whatsapp.reply_button import handle_button_reply
from app.services.whatsapp.save_message import save_conversation_message
from app.utils.Enums.user_enum import SenderType


# -----------------------------
# Helper: Convert WhatsApp timestamp to UTC datetime
# -----------------------------
def convert_wa_timestamp(wa_timestamp: str | None) -> datetime:
    """
    Converts WhatsApp timestamp to datetime with UTC timezone.
    If timestamp is missing, fallback to current UTC time.
    """
    if wa_timestamp is None:
        return datetime.now(timezone.utc)
    try:
        # WhatsApp timestamp is usually in seconds (string), convert to int
        return datetime.fromtimestamp(int(wa_timestamp), tz=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)

async def handle_whatsapp_events(request: Request):
    try:
        event = await request.json()
        entry = event.get("entry")
        if not entry:
            return {"status": "ok"}

        changes = entry[0].get("changes")
        if not changes:
            return {"status": "ok"}

        value = changes[0].get("value", {})
        messages = value.get("messages")
        if not messages:
            return {"status": "ok"}

        first_message = messages[0]
        thread_id = first_message.get("from")
        if not thread_id:
            return {"status": "ok"}

        # -----------------------------
        # Handle button replies first
        # -----------------------------
        if (
            first_message.get("type") == "interactive"
            and first_message.get("interactive", {}).get("type") == "button_reply"
        ):
            # Convert timestamp for UI consistency
            wa_timestamp = first_message.get("timestamp")
            user_message_time = convert_wa_timestamp(wa_timestamp)

            await handle_button_reply(first_message, timestamp=user_message_time)
            return {"status": "ok"}

        # -----------------------------
        # Normal text message
        # -----------------------------
        msg_text = (
            first_message.get("text", {}).get("body")
            if isinstance(first_message.get("text"), dict)
            else first_message.get("text")
        ) or ""

        profile_name = (
            value.get("contacts", [{}])[0].get("profile", {}).get("name") or "iShout"
        )

        app = request.app
        whatsapp_agent = getattr(app.state, "whatsapp_agent", None)
        if not whatsapp_agent:
            raise HTTPException(
                status_code=503,
                detail="WhatsApp agent not initialized",
            )

        # -----------------------------
        # Load or initialize user state
        # -----------------------------
        stored_state = await get_user_state(thread_id)
        state = stored_state or {}

        conversation_round = await get_conversation_round(thread_id) or 1

        if state.get("done") and state.get("acknowledged"):
            conversation_round = await increment_conversation_round(thread_id)
            if conversation_round > 1:
                await cleanup_old_checkpoints(thread_id, conversation_round)
            state = await reset_user_state(thread_id)

        checkpoint_thread_id = f"{thread_id}-r{conversation_round}"

        # Update state
        state.update(
            {
                "user_message": msg_text,
                "event_data": value,
                "thread_id": thread_id,
                "sender_id": thread_id,
                "name": profile_name or state.get("name"),
            }
        )

        # -----------------------------
        # Convert WhatsApp timestamp
        # -----------------------------
        wa_timestamp = first_message.get("timestamp")
        user_message_time = convert_wa_timestamp(wa_timestamp)

        # -----------------------------
        # Save message to DB
        # -----------------------------
        await save_conversation_message(
            thread_id=thread_id,
            username=profile_name,
            sender=SenderType.USER.value,
            message=state.get("user_message"),
            timestamp=user_message_time,
        )

        # -----------------------------
        # Broadcast to UI
        # -----------------------------
        await ws_manager.broadcast_event(
            "whatsapp.message",
            {
                "thread_id": thread_id,
                "sender": "USER",
                "message": state.get("user_message"),
                "timestamp": user_message_time.isoformat(),
            },
        )

        # -----------------------------
        # Process AI agent
        # -----------------------------
        final_state = await whatsapp_agent.ainvoke(
            state,
            config={"configurable": {"thread_id": checkpoint_thread_id}},
        )

        if final_state:
            await update_user_state(thread_id, final_state)

        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Webhook processing failed: {str(e)}"
        ) from e

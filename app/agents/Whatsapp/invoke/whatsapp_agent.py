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
from app.services.websocket_manager import ws_manager
from app.services.whatsapp.reply_button import handle_button_reply
from app.services.whatsapp.save_message import save_conversation_message
from app.utils.Enums.user_enum import SenderType


async def handle_whatsapp_events(request: Request):
    print("Entering into handle_whatsapp_events")
    print("--------------------------------")
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

        # Handle button replies separately
        if (
            first_message.get("type") == "interactive"
            and first_message.get("interactive", {}).get("type") == "button_reply"
        ):
            await handle_button_reply(first_message)
            return {"status": "ok"}

        thread_id = first_message.get("from")
        if not thread_id:
            return {"status": "ok"}

        # Extract user text
        msg_text = (
            first_message.get("text", {}).get("body")
            if isinstance(first_message.get("text"), dict)
            else first_message.get("text")
        ) or ""

        profile_name = (
            value.get("contacts", [{}])[0].get("profile", {}).get("name") or "iShout"
        )

        # Get the default WhatsApp agent
        app = request.app
        whatsapp_agent = getattr(app.state, "whatsapp_agent", None)
        if not whatsapp_agent:
            raise HTTPException(
                status_code=503,
                detail="WhatsApp agent not initialized",
            )

        # Retrieve stored state
        stored_state = await get_user_state(thread_id)
        state = stored_state or {}

        # Conversation round handling
        conversation_round = await get_conversation_round(thread_id) or 1
        if state.get("done") and state.get("acknowledged"):
            conversation_round = await increment_conversation_round(thread_id)
            if conversation_round > 1:
                await cleanup_old_checkpoints(thread_id, conversation_round)
            state = await reset_user_state(thread_id)

        checkpoint_thread_id = f"{thread_id}-r{conversation_round}"

        # Update state with incoming message
        state.update(
            {
                "user_message": msg_text,
                "event_data": value,
                "thread_id": thread_id,
                "sender_id": thread_id,
                "name": profile_name or state.get("name"),
            }
        )

        # Save user message
        await save_conversation_message(
            thread_id=thread_id,
            username=profile_name,
            sender=SenderType.USER.value,
            message=state.get("user_message"),
        )
        print("Conversation message saved")
        print("--------------------------------")

        # Broadcast to WebSocket
        await ws_manager.broadcast_event(
            "whatsapp.message",
            {
                "thread_id": thread_id,
                "sender": "USER",
                "message": state.get("user_message"),
                "timestamp": datetime.now(timezone.utc),
            },
        )

        # **Routing decision**
        conversation_mode = state.get("conversation_mode", "DEFAULT")

        if conversation_mode == "NEGOTIATION":
            print("Routing to Negotiation Agent")
            # Default agent will NOT process negotiation messages
            final_state = await Negotiation_invoke(
                state,
                config={"configurable": {"thread_id": checkpoint_thread_id}},
            )
        else:
            print("Routing to Default WhatsApp Agent")
            final_state = await whatsapp_agent.ainvoke(
                state,
                config={"configurable": {"thread_id": checkpoint_thread_id}},
            )

        # Update state
        if final_state:
            await update_user_state(thread_id, final_state)

        return {"status": "ok"}

    except Exception as e:
        print("Error in handle_whatsapp_events")
        print("--------------------------------")
        print(e)
        print("--------------------------------")
        raise HTTPException(
            status_code=500, message=f"Webhook processing failed: {str(e)}"
        ) from e

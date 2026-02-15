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
from app.services.websocket_manager import ws_manager
from app.services.whatsapp.reply_button import handle_button_reply
from app.services.whatsapp.save_message import save_conversation_message
from app.utils.Enums.user_enum import SenderType
from app.utils.printcolors import Colors


async def extract_message_info(first_message: dict, value: dict):
    thread_id = first_message.get("from")
    msg_text = (
        first_message.get("text", {}).get("body")
        if isinstance(first_message.get("text"), dict)
        else first_message.get("text")
    ) or ""
    profile_name = (
        value.get("contacts", [{}])[0].get("profile", {}).get("name") or "iShout"
    )
    return thread_id, msg_text, profile_name


async def process_negotiation_agent(state: dict, app):
    negotiation_state = await get_negotiation_state(state.get("thread_id"))
    if (
        negotiation_state
        and negotiation_state.get("conversation_mode") == "NEGOTIATION"
        and not negotiation_state.get("agent_paused")
    ):
        print(
            f"{Colors.GREEN}Routing to Negotiation Agent for thread {state.get('thread_id')}"
        )
        negotiation_state.update(
            {
                "user_message": state.get("user_message"),
                "thread_id": state.get("thread_id"),
                "sender_id": state.get("sender_id"),
                "name": state.get("name"),
            }
        )
        final_state = await Negotiation_invoke(
            negotiation_state,
            app,
            config={"configurable": {"thread_id": state.get("thread_id")}},
        )
        if final_state:
            await update_negotiation_state(state.get("thread_id"), final_state)
            print(
                f"{Colors.GREEN}Negotiation agent completed for thread {state.get('thread_id')}"
            )
            print("--------------------------------")
        return True
    return False


async def process_default_agent(
    thread_id: str, msg_text: str, profile_name: str, event_data: dict, app
):
    whatsapp_agent = getattr(app.state, "whatsapp_agent", None)
    if not whatsapp_agent:
        raise HTTPException(status_code=503, detail="WhatsApp agent not initialized")

    stored_state = await get_user_state(thread_id) or {}
    conversation_round = await get_conversation_round(thread_id) or 1

    if stored_state.get("done") and stored_state.get("acknowledged"):
        conversation_round = await increment_conversation_round(thread_id)
        if conversation_round > 1:
            await cleanup_old_checkpoints(thread_id, conversation_round)
        stored_state = await reset_user_state(thread_id)

    checkpoint_thread_id = f"{thread_id}-r{conversation_round}"
    stored_state.update(
        {
            "user_message": msg_text,
            "event_data": event_data,
            "thread_id": thread_id,
            "sender_id": thread_id,
            "name": profile_name or stored_state.get("name"),
        }
    )

    final_state = await whatsapp_agent.ainvoke(
        stored_state, config={"configurable": {"thread_id": checkpoint_thread_id}}
    )
    if final_state:
        await update_user_state(thread_id, final_state)


async def whatsapp_events_with_state(request: Request):
    print(f"{Colors.GREEN}Entering whatsapp_events_with_state")
    print("--------------------------------")
    try:
        event = await request.json()
        entry = event.get("entry", [])
        if not entry:
            return {"status": "ok"}
        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "ok"}
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return {"status": "ok"}
        first_message = messages[0]
        return first_message, value
    except Exception as e:
        print(f"{Colors.RED}Error in handle_whatsapp_events_with_state: {e}")
        print("--------------------------------")
        raise HTTPException(
            status_code=500, detail=f"Webhook processing failed: {str(e)}"
        ) from e


async def handle_whatsapp_events(request: Request):
    print(f"{Colors.GREEN}Entering handle_whatsapp_events")
    print("--------------------------------")
    try:
        first_message, value = await whatsapp_events_with_state(request)
        if (
            first_message.get("type") == "interactive"
            and first_message.get("interactive", {}).get("type") == "button_reply"
        ):
            await handle_button_reply(first_message)
            return {"status": "ok"}
        # Extract message info
        thread_id, msg_text, profile_name = await extract_message_info(
            first_message, value
        )

        if not thread_id:
            return {"status": "ok"}
        await save_conversation_message(
            thread_id=thread_id,
            username=profile_name,
            sender=SenderType.USER.value,
            message=msg_text,
        )
        await ws_manager.broadcast_event(
            "whatsapp.message",
            {
                "thread_id": thread_id,
                "sender": "USER",
                "message": msg_text,
                "timestamp": datetime.now(timezone.utc),
            },
        )

        routed = await process_negotiation_agent(
            {
                "user_message": msg_text,
                "thread_id": thread_id,
                "sender_id": thread_id,
                "name": profile_name,
            },
            request.app,
        )
        if routed:
            return {"status": "ok"}
        await process_default_agent(
            thread_id, msg_text, profile_name, value, request.app
        )
        print(f"{Colors.YELLOW}Exiting handle_whatsapp_events")
        print("--------------------------------")
        return {"status": "ok"}

    except Exception as e:
        print(f"{Colors.RED}Error in handle_whatsapp_events: {e}")
        print("--------------------------------")
        raise HTTPException(
            status_code=500, detail=f"Webhook processing failed: {str(e)}"
        ) from e

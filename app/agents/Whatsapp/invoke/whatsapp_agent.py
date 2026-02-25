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
from app.utils.printcolors import Colors


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

    msg_text = (
        first_message.get("text", {}).get("body")
        if isinstance(first_message.get("text"), dict)
        else first_message.get("text")
    ) or ""

    profile_name = (
        value.get("contacts", [{}])[0].get("profile", {}).get("name") or "iShout"
    )

    return first_message, thread_id, msg_text, profile_name, value


async def process_incoming_message(thread_id, profile_name, msg_text):
    await save_conversation_message(
        thread_id=thread_id,
        username=profile_name,
        sender=SenderType.USER.value,
        message=msg_text,
    )

    print(f"{Colors.GREEN}Conversation message saved")
    print("--------------------------------")

    await ws_manager.broadcast_event(
        "whatsapp.message",
        {
            "thread_id": thread_id,
            "sender": "USER",
            "message": msg_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


async def handle_negotiation_agent(request, thread_id, msg_text, profile_name):
    print(f"{Colors.GREEN}Entering into handle_negotiation_agent")
    print("--------------------------------")
    negotiation_state = await get_negotiation_state(thread_id)
    print(f"{Colors.CYAN}Negotiation state: {negotiation_state}")
    print("--------------------------------")
    if (
        not negotiation_state
        or negotiation_state.get("agent_paused")
        or negotiation_state.get("negotiation_completed")
    ):
        print(f"{Colors.RED}No active negotiation state or agent paused/completed")
        print("--------------------------------")
        print(f"{Colors.YELLOW}Exiting from handle_negotiation_agent")
        print("--------------------------------")
        return False

    print(f"{Colors.CYAN}Routing to Negotiation Agent")
    print("--------------------------------")

    # Maintain a rolling window of recent conversation history (USER + AI).
    # Normalize to list (Mongo may return history as dict or other type).
    history = get_history_list(negotiation_state)
    history.append({"sender_type": "USER", "message": msg_text})
    # Keep only the last N messages to avoid unbounded growth
    MAX_HISTORY_LENGTH = 20
    if len(history) > MAX_HISTORY_LENGTH:
        history = history[-MAX_HISTORY_LENGTH:]

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
    print("Routing to Default WhatsApp Agent")
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
    print(f"{Colors.GREEN}Entering into handle_whatsapp_events")
    print("--------------------------------")

    try:
        event = await request.json()
        first_message, thread_id, msg_text, profile_name, value = (
            extract_whatsapp_message(event)
        )
        if not first_message or not thread_id:
            return {"status": "ok"}
        if (
            first_message.get("type") == "interactive"
            and first_message.get("interactive", {}).get("type") == "button_reply"
        ):
            await handle_button_reply(first_message)
            return {"status": "ok"}

        # Save + broadcast
        await process_incoming_message(thread_id, profile_name, msg_text)

        # negotiation agent
        negotiation_handled = await handle_negotiation_agent(
            request, thread_id, msg_text, profile_name
        )
        if negotiation_handled:
            return {"status": "ok"}

        # Otherwise default agent
        await handle_default_agent(request, thread_id, msg_text, profile_name, value)
        print(f"{Colors.YELLOW}Exiting from handle_whatsapp_events")
        print("--------------------------------")
        return {"status": "ok"}

    except Exception as e:
        print(f"{Colors.RED}Error in handle_whatsapp_events: {e}")
        print("--------------------------------")

        raise HTTPException(
            status_code=500,
            detail=f"Webhook processing failed: {str(e)}",
        ) from e

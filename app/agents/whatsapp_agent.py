from fastapi import Request, HTTPException
from app.agents.nodes.state import (
    cleanup_old_checkpoints,
    get_conversation_round,
    increment_conversation_round,
)
from app.agents.state.get_user_state import get_user_state
from app.agents.state.update_user_state import update_user_state
from app.agents.state.reset_state import reset_user_state
from app.services.whatsapp.reply_button import handle_button_reply


async def handle_whatsapp_events(request: Request):
    print("Entering handle_whatsapp_events")
    try:
        event = await request.json()
        entry = event.get("entry")
        print(f"Entry: {entry}")
        if not entry:
            return {"status": "ok"}

        changes = entry[0].get("changes")
        if not changes:
            return {"status": "ok"}
        print(f"Changes: {changes}")

        value = changes[0].get("value", {})
        messages = value.get("messages")
        if not messages:
            return {"status": "ok"}
        print(f"Value: {value}")
        print(f"Messages: {messages}")
        first_message = messages[0]
        print(f"First message: {first_message}")
        if (
            first_message.get("type") == "interactive"
            and first_message.get("interactive", {}).get("type") == "button_reply"
        ):
            print("Handling button reply")
            await handle_button_reply(first_message)
            return {"status": "ok"}

        thread_id = first_message.get("from")
        if not thread_id:
            return {"status": "ok"}
        print(f"Thread ID: {thread_id}")
        msg_text = (
            first_message.get("text", {}).get("body")
            if isinstance(first_message.get("text"), dict)
            else first_message.get("text")
        ) or ""
        print(f"Message text: {msg_text}")
        profile_name = value.get("contacts", [{}])[0].get("profile", {}).get("name")
        print(f"Profile name: {profile_name}")
        app = request.app
        print(f"App: {app}")
        whatsapp_agent = getattr(app.state, "whatsapp_agent", None)
        if not whatsapp_agent:
            raise HTTPException(
                status_code=503,
                detail="WhatsApp agent not initialized",
            )
        print("Getting user state")
        stored_state = await get_user_state(thread_id)
        state = stored_state or {}
        print(f"State: {state}")
        conversation_round = await get_conversation_round(thread_id)
        print(f"Conversation round: {conversation_round}")
        if not conversation_round:
            conversation_round = 1
        print(f"State done: {state.get('done')}")
        print(f"State acknowledged: {state.get('acknowledged')}")
        if state.get("done") and state.get("acknowledged"):
            print("Incrementing conversation round")
            conversation_round = await increment_conversation_round(thread_id)
            print(f"Conversation round after increment: {conversation_round}")
            if conversation_round > 1:
                await cleanup_old_checkpoints(thread_id, conversation_round)
            state = await reset_user_state(thread_id)
            print(f"State after reset: {state}")
        checkpoint_thread_id = f"{thread_id}-r{conversation_round}"
        print(f"Checkpoint thread ID: {checkpoint_thread_id}")
        state.update(
            {
                "user_message": msg_text,
                "event_data": value,
                "thread_id": thread_id,
                "sender_id": thread_id,
                "name": profile_name or state.get("name"),
            }
        )
        print(f"State after update: {state}")
        final_state = await whatsapp_agent.ainvoke(
            state,
            config={"configurable": {"thread_id": checkpoint_thread_id}},
        )
        print(f"Final state: {final_state}")
        if final_state:
            await update_user_state(thread_id, final_state)
            print("User state updated")
        print("Exiting handle_whatsapp_events successfully")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Webhook processing failed: {str(e)}"
        ) from e

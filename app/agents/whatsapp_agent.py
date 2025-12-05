from fastapi import Request
import logging
from app.agents.nodes.state import get_user_state, reset_user_state, update_user_state
from app.db.sqlite import build_whatsapp_agent


async def handle_whatsapp_events(request: Request):
    try:
        event = await request.json()
        event_data = event["entry"][0]["changes"][0]["value"]

        # Ignore non-message events
        if "messages" not in event_data or not event_data.get("messages"):
            return {"status": "ok"}

        first_message = event_data["messages"][0]
        thread_id = first_message.get("from")
        user_text = (
            first_message.get("text", {}).get("body")
            if isinstance(first_message.get("text"), dict)
            else first_message.get("text")
        ) or ""

        if not thread_id:
            return {"status": "error", "message": "No sender ID found"}

        # Load user state
        state = await get_user_state(thread_id)
        state.pop("_id", None)

        # Reset if conversation is fully done
        if state.get("done") and state.get("reply_sent"):
            state = await reset_user_state(thread_id)

        # Update state with latest message
        state.update(
            {
                "user_message": user_text,
                "event_data": event_data,
                "thread_id": thread_id,
                "sender_id": thread_id,
            }
        )

        # Reset if conversation was done but reply not sent
        if state.get("done") and not state.get("reply_sent"):
            state = await reset_user_state(thread_id)
            state.update(
                {
                    "user_message": user_text,
                    "event_data": event_data,
                    "thread_id": thread_id,
                    "sender_id": thread_id,
                }
            )

        event_data_backup = state.get("event_data")
        thread_id_backup = state.get("thread_id")
        state = await update_user_state(thread_id, state)
        state["event_data"] = event_data_backup
        state["thread_id"] = thread_id_backup
        state["user_message"] = user_text

        # Build and invoke LangGraph agent
        whatsapp_agent = await build_whatsapp_agent()
        final_state = await whatsapp_agent.ainvoke(
            state,
            config={
                "configurable": {
                    "thread_id": thread_id,
                }
            },
        )

        # Persist final state after agent run
        if final_state:
            await update_user_state(thread_id, final_state)

        return {"status": "ok"}

    except Exception as e:
        logging.exception("Error handling WhatsApp event")
        return {"status": "error", "message": str(e)}

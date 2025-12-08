from fastapi import Request
import logging
from app.agents.nodes.state import get_user_state, reset_user_state, update_user_state
from app.db.sqlite import build_whatsapp_agent


async def handle_whatsapp_events(request: Request):
    try:
        event = await request.json()
        event_data = event["entry"][0]["changes"][0]["value"]

        # Ignore statuses and non-message updates
        if "messages" not in event_data or not event_data["messages"]:
            return {"status": "ok"}

        first_message = event_data["messages"][0]
        thread_id = first_message.get("from")

        # Extract message text safely
        msg_text = (
            first_message.get("text", {}).get("body")
            if isinstance(first_message.get("text"), dict)
            else first_message.get("text")
        ) or ""

        if not thread_id:
            return {"status": "error", "message": "No sender ID found"}

        # Load state
        state = await get_user_state(thread_id)
        state.pop("_id", None)

        # ---- FIXED: Do NOT reset reply_sent unless starting new ----
        if state.get("reply_sent") is True and state.get("ready_for_campaign") is True:
            # This means user sent a NEW message after summary
            await reset_user_state(thread_id)
            state = await get_user_state(thread_id)
            state.pop("_id", None)

        # Update state with new message
        state["user_message"] = msg_text
        state["event_data"] = event_data
        state["thread_id"] = thread_id
        state["sender_id"] = thread_id

        # Only reset reply_sent if this is a NEW user request
        if "reply_sent" not in state or state.get("reply_sent") is True:
            state["reply_sent"] = False

        await update_user_state(thread_id, state)

        # ---- Run LangGraph Agent ----
        whatsapp_agent = await build_whatsapp_agent()

        final_state = await whatsapp_agent.ainvoke(
            state,
            config={"configurable": {"thread_id": thread_id}},
        )

        if final_state:
            await update_user_state(thread_id, final_state)

        return {"status": "ok"}

    except Exception as e:
        logging.exception("Error handling WhatsApp event")
        return {"status": "error", "message": str(e)}

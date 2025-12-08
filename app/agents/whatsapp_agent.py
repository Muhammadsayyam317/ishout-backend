from fastapi import Request
import logging
from app.agents.nodes.state import get_user_state, update_user_state
from app.db.sqlite import build_whatsapp_agent
from app.services.whatsapp_user import create_whatsapp_user


async def handle_whatsapp_events(request: Request):
    try:
        event = await request.json()
        event_data = event["entry"][0]["changes"][0]["value"]

        if "messages" not in event_data or not event_data["messages"]:
            return {"status": "ok"}

        first_message = event_data["messages"][0]
        thread_id = first_message.get("from")

        msg_text = (
            first_message.get("text", {}).get("body")
            if isinstance(first_message.get("text"), dict)
            else first_message.get("text")
        ) or ""

        if not thread_id:
            return {"status": "error", "message": "No sender ID found"}

        profile_name = (
            event_data.get("contacts", [{}])[0].get("profile", {}).get("name")
        )
        await create_whatsapp_user(thread_id, profile_name)

        whatsapp_agent = await build_whatsapp_agent()
        stored_state = await get_user_state(thread_id)
        state = stored_state or {}

        state.update(
            {
                "user_message": msg_text,
                "event_data": event_data,
                "thread_id": thread_id,
                "sender_id": thread_id,
            }
        )

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

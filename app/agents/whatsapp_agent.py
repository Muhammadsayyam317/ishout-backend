from fastapi import Request, HTTPException
from app.agents.nodes.state import (
    get_conversation_round,
    increment_conversation_round,
)
from app.db.sqlite import build_whatsapp_agent
from app.agents.state.get_user_state import get_user_state
from app.agents.state.update_user_state import update_user_state
from app.agents.state.reset_state import reset_user_state


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

        whatsapp_agent = await build_whatsapp_agent()
        stored_state = await get_user_state(thread_id)
        state = stored_state or {}
        conversation_round = await get_conversation_round(thread_id)
        if state.get("done") and state.get("acknowledged"):
            conversation_round = await increment_conversation_round(thread_id)
            state = await reset_user_state(thread_id)

        checkpoint_thread_id = f"{thread_id}-r{conversation_round}"
        state.update(
            {
                "user_message": msg_text,
                "event_data": event_data,
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
        return {"status": "ok"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

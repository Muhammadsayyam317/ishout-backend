from fastapi import Request
from app.agents.nodes.state import get_user_state
from app.db.sqlite import build_whatsapp_agent
from app.utils.chat_history import save_chat_message


USER_STATES = {}


async def handle_whatsapp_events(request: Request):
    event = await request.json()
    event_data = event["entry"][0]["changes"][0]["value"]

    if "messages" not in event_data:
        return {"status": "ok", "message": "Status update, skipping"}
    if not event_data.get("messages"):
        return {"status": "ok", "message": "No messages to process"}

    # Get thread_id and user text from the first message
    first_message = event_data["messages"][0]
    thread_id = first_message.get("from")
    user_text = (
        first_message.get("text", {}).get("body")
        if isinstance(first_message.get("text"), dict)
        else first_message.get("text")
    ) or ""

    if not thread_id:
        return {"status": "error", "message": "No sender ID found in message"}
    await save_chat_message(
        thread_id=thread_id,
        role="user",
        content=user_text,
        metadata={"source": "whatsapp_webhook"},
    )
    state = get_user_state(thread_id)
    # add message into the state
    state["user_message"] = user_text
    state["event_data"] = event_data
    state["thread_id"] = thread_id
    state["sender_id"] = thread_id

    whatsapp_agent = await build_whatsapp_agent()
    final_state = await whatsapp_agent.ainvoke(
        state, config={"configurable": {"thread_id": thread_id}}
    )
    USER_STATES[thread_id] = final_state
    reply_text = (final_state or {}).get("reply")
    if reply_text:
        await save_chat_message(
            thread_id=thread_id,
            role="assistant",
            content=reply_text,
            metadata={"source": "whatsapp_agent"},
        )

    return {"status": "ok"}

from fastapi import Request
from app.agents.nodes.graph import whatsapp_agent
from app.utils.chat_history import save_chat_message


async def handle_whatsapp_events(request: Request):
    event = await request.json()
    event_data = event["entry"][0]["changes"][0]["value"]

    # Check if this is a message event (not a status update)
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

    # Persist user message to Mongo for long-term memory
    await save_chat_message(
        thread_id=thread_id,
        role="user",
        content=user_text,
        metadata={"source": "whatsapp_webhook"},
    )

    state = {"event_data": event_data}
    final_state = await whatsapp_agent.ainvoke(
        state, config={"configurable": {"thread_id": thread_id}}
    )

    # Persist assistant reply (if any)
    reply_text = (final_state or {}).get("reply")
    if reply_text:
        await save_chat_message(
            thread_id=thread_id,
            role="assistant",
            content=reply_text,
            metadata={"source": "whatsapp_agent"},
        )

    return {"status": "ok"}

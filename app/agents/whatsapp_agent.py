from fastapi import Request
from app.agents.nodes.graph import whatsapp_agent


async def handle_whatsapp_events(request: Request):
    event = await request.json()
    event_data = event["entry"][0]["changes"][0]["value"]

    # Check if this is a message event (not a status update)
    if "messages" not in event_data:
        return {"status": "ok", "message": "Status update, skipping"}
    if not event_data.get("messages"):
        return {"status": "ok", "message": "No messages to process"}

    # Get thread_id from the first message
    first_message = event_data["messages"][0]
    thread_id = first_message.get("from")

    if not thread_id:
        return {"status": "error", "message": "No sender ID found in message"}

    state = {"event_data": event_data}
    await whatsapp_agent.ainvoke(
        state, config={"configurable": {"thread_id": thread_id}}
    )
    return {"status": "ok"}

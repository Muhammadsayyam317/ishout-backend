from fastapi import Request
from app.agents.nodes.state import get_user_state, update_user_state
from app.db.sqlite import build_whatsapp_agent
from app.utils.chat_history import save_chat_message


async def handle_whatsapp_events(request: Request):
    event = await request.json()
    event_data = event["entry"][0]["changes"][0]["value"]
    if "messages" not in event_data:
        return {"status": "ok"}
    # Extract user + message
    first_message = event_data["messages"][0]
    thread_id = first_message.get("from")
    user_text = first_message.get("text", {}).get("body") or ""
    # Log message
    await save_chat_message(
        thread_id=thread_id,
        role="user",
        content=user_text,
        metadata={"source": "whatsapp_webhook"},
    )
    # Load session (MongoDB)
    state = await get_user_state(thread_id)
    # Inject new values
    state["user_message"] = user_text
    state["event_data"] = event_data
    state["thread_id"] = thread_id
    state["sender_id"] = thread_id

    # Run AI agent
    whatsapp_agent = await build_whatsapp_agent()
    final_state = await whatsapp_agent.ainvoke(
        state, config={"configurable": {"thread_id": thread_id}}
    )

    # Save updated session in MongoDB
    if final_state:
        await update_user_state(thread_id, final_state)
    return {"status": "ok"}

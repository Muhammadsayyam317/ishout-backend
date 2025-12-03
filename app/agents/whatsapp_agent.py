from fastapi import HTTPException, Request
from app.agents.nodes.state import get_user_state, update_user_state
from app.db.sqlite import build_whatsapp_agent
from app.utils.chat_history import save_chat_message
import logging


async def handle_whatsapp_events(request: Request):
    event = await request.json()
    try:
        event_data = event["entry"][0]["changes"][0]["value"]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    if "messages" not in event_data or not event_data.get("messages"):
        return {"status": "ok", "message": "no messages"}

    first = event_data["messages"][0]
    thread_id = first.get("from")
    message_id = first.get("id")
    user_text = (
        (first.get("text", {}) or {}).get("body")
        if isinstance(first.get("text"), dict)
        else first.get("text") or ""
    )

    if not thread_id:
        raise HTTPException(status_code=400, detail="missing sender id")

    # idempotency: ignore same message repeated
    session = await get_user_state(thread_id)
    last_mid = session.get("last_message_id")
    if last_mid == message_id:
        logging.info("Duplicate webhook for same message_id -> ignoring")
        return {"status": "ok", "ignored_duplicate": True}

    # persist incoming user message for audit
    await save_chat_message(
        thread_id=thread_id,
        role="user",
        content=user_text,
        metadata={"source": "whatsapp_webhook", "message_id": message_id},
    )

    # update session with this message id and last_active
    await update_user_state(
        thread_id,
        {
            "last_message_id": message_id,
            "user_message": user_text,
            "event_data": event_data,
        },
    )

    # run agent
    whatsapp_agent = await build_whatsapp_agent()
    # pass current state document into graph run — graph nodes will perform sends
    final_state = await whatsapp_agent.ainvoke(
        session, config={"configurable": {"thread_id": thread_id}}
    )

    # persist final_state back into session DB
    if final_state:
        await update_user_state(thread_id, final_state)

    return {"status": "ok"}

from fastapi import Request
from app.services.whatsapp.webhook_parser import parse_whatsapp_message
from app.services.whatsapp.reply_button import handle_button_reply
from app.services.whatsapp.save_message import save_conversation_message
from app.agents.flow.whatsapp_agent import run_whatsapp_agent
from app.utils.Enums.user_enum import SenderType


async def handle_whatsapp_events(request: Request):
    event = await request.json()
    parsed = parse_whatsapp_message(event)

    if not parsed:
        return {"status": "ok"}
    if parsed["type"] == "interactive":
        await handle_button_reply(parsed["interactive"])
        return {"status": "ok"}

    await save_conversation_message(
        thread_id=parsed["thread_id"],
        sender=SenderType.USER.value,
        message=parsed["text"],
        node="incoming_webhook",
    )

    await run_whatsapp_agent(
        thread_id=parsed["thread_id"],
        msg_text=parsed["text"],
        profile_name=parsed["profile_name"],
        raw_event=parsed["raw"],
        app=request.app,
    )

    return {"status": "ok"}

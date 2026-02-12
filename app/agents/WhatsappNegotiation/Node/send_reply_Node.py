from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.config.credentials_config import config
import httpx
from app.services.whatsapp.save_message import save_conversation_message
from app.utils.Enums.user_enum import SenderType


async def send_whatsapp_reply_node(state: WhatsappNegotiationState):
    final_reply = state.get("final_reply")
    thread_id = state.get("thread_id")
    if not final_reply or not thread_id:
        print("[send_whatsapp_reply_node] Missing final_reply or thread_id")
        return state
    headers = {
        "Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": thread_id,
        "type": "text",
        "text": {"body": final_reply},
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://graph.facebook.com/v22.0/967002123161751/messages",
                headers=headers,
                json=payload,
            )
        print("[send_whatsapp_reply_node] Response:", response.json())
    except Exception as e:
        print(f"[send_whatsapp_reply_node] Error sending WhatsApp message: {e}")

        await save_conversation_message(
            thread_id=state["thread_id"],
            username="AI Negotiator",
            sender=SenderType.AI.value,
            message=final_reply,
        )

    return state

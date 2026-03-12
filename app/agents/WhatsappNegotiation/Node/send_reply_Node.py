from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.config.credentials_config import config
import httpx
from app.services.whatsapp.save_message import save_conversation_message
from app.utils.Enums.user_enum import SenderType
from app.utils.printcolors import Colors


async def send_whatsapp_reply_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering into send_whatsapp_reply_node")
    print("--------------------------------")
    final_reply = state.get("final_reply")
    thread_id = state.get("thread_id")
    if not final_reply or not thread_id:
        print("[send_whatsapp_reply_node] Missing final_reply or thread_id")
        return state
    headers = {
        "Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}",
        "Content-Type": "application/json",
    }

    base_url = "https://graph.facebook.com/v22.0/967002123161751/messages"

    text_payload = {
        "messaging_product": "whatsapp",
        "to": thread_id,
        "type": "text",
        "text": {"body": final_reply},
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            text_response = await client.post(
                base_url,
                headers=headers,
                json=text_payload,
            )

            await save_conversation_message(
                thread_id=state["thread_id"],
                username="AI Negotiator",
                sender=SenderType.AI.value,
                message=final_reply,
            )

            print("[send_whatsapp_reply_node] Text response:", text_response.json())

            # If we have a brief PDF uploaded to Meta, send it as a document message.
            brief_media_id = state.get("brief_media_id")
            if brief_media_id:
                filename = state.get("brief_media_filename") or "campaign_brief.pdf"
                document_payload = {
                    "messaging_product": "whatsapp",
                    "to": thread_id,
                    "type": "document",
                    "document": {
                        "id": brief_media_id,
                        "filename": filename,
                        "caption": "Campaign brief",
                    },
                }

                document_response = await client.post(
                    base_url,
                    headers=headers,
                    json=document_payload,
                )
                print(
                    "[send_whatsapp_reply_node] Document response:",
                    document_response.json(),
                )

        print(f"{Colors.YELLOW} Exiting from send_whatsapp_reply_node")
        print("--------------------------------")
    except Exception as e:
        print(
            f"{Colors.RED}[send_whatsapp_reply_node] Error sending WhatsApp message: {e}"
        )
    return state

import httpx
from app.config.credentials_config import config
from fastapi import Body
from app.services.whatsapp.save_negotiation_message import save_negotiation_message
from app.utils.Enums.user_enum import SenderType


async def NegotiationInitialMessage(payload: dict = Body(...)):
    to = payload["to"]
    influencer_name = payload["influencer_name"]
    if not to or not influencer_name:
        print("[NegotiationInitialMessage] Missing 'to' or 'influencer_name'")
        return {"status": "error", "message": "Missing 'to' or 'influencer_name'"}
    # campaign_name = payload["campaign_name"]
    print("Payload: ", payload)
    print("To: ", to)
    print("Influencer Name: ", influencer_name)
    # print("Campaign Name: ", campaign_name)
    print("--------------------------------")

    headers = {
        "Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}",
        "Content-Type": "application/json",
    }

    payload_meta = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": "negotiation",
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": influencer_name},
                    ],
                }
            ],
        },
    }
    print("Payload Meta: ", payload_meta)
    print("--------------------------------")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://graph.facebook.com/v22.0/967002123161751/messages",
                headers=headers,
                json=payload_meta,
            )
        print("--------------------------------")
        print("Response: ", response.json())
        print("--------------------------------")
    except Exception as e:
        print(f"[NegotiationInitialMessage] Error sending WhatsApp message: {e}")
        return {"status": "error", "message": f"Error sending WhatsApp message: {e}"}

    await save_negotiation_message(
        thread_id=to,
        username=influencer_name,
        sender=SenderType.AI.value,
        message="""Hi this is the collaboration team from iShout.\n\nWe’d love to work with you on an upcoming campaign that matches your profile.\n\nJust reply 'interested,' and we will share the campaign brief and next steps.""",
        agent_paused=False,
        human_takeover=False,
        conversation_mode="NEGOTIATION",
    )
    return {"status": "success"}

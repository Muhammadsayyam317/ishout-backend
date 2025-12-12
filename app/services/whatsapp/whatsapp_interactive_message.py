import httpx
from fastapi import HTTPException
from app.config.credentials_config import config


async def send_whatsapp_interactive_message(
    recipient_id: str, message_text: str, influencer: dict
) -> bool:

    print(
        f"[send_whatsapp_message] Sending message to {recipient_id} with content: {influencer}"
    )
    headers = {
        "Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}",
        "Content-Type": "application/json",
    }

    message_payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {"type": "image", "image": {"link": influencer.get("pic")}},
            "body": {
                "text": (
                    f"@{influencer.get('username')}\n"
                    f"Followers: {influencer.get('followers')}\n"
                    f"Country: {influencer.get('country')}\n"
                    f"Pricing: {influencer.get('pricing')}\n"
                    f"Profile: {influencer.get('pic')}\n"
                    f"Link: https://www.instagram.com/{influencer.get('username')}"
                )
            },
            "footer": {"text": message_text},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": f"approve_{influencer.get('_id')}",
                            "title": "Approve 👍",
                        },
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": f"reject_{influencer.get('_id')}",
                            "title": "Reject 🚫",
                        },
                    },
                ]
            },
        },
    }

    print(
        f"[send_whatsapp_message] Sending message to {recipient_id} with content: {message_payload}"
    )
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://graph.facebook.com/v24.0/912195958636325/messages",
                headers=headers,
                json=message_payload,
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error: {response.status_code}, {response.text}",
                )
            return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

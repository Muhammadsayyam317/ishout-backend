import httpx
from app.config.credentials_config import config


async def send_whatsapp_interactive_message(
    recipient_id: str,
    message_text: str,
    influencer: dict,
) -> bool:

    access_token = config.META_WHATSAPP_ACCESSSTOKEN

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    username = influencer.get("username") or "unknown"
    followers = influencer.get("followers") or "N/A"
    country = influencer.get("country") or "N/A"
    pricing = influencer.get("pricing") or "N/A"
    pic = influencer.get("pic")

    interactive = {
        "type": "button",
        "body": {
            "text": (
                f"@{username}\n"
                f"Followers: {followers}\n"
                f"Country: {country}\n"
                f"Pricing: {pricing}\n"
                f"Link: https://www.instagram.com/{username}"
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
    }

    if pic:
        interactive["header"] = {
            "type": "image",
            "image": {"link": pic},
        }

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "interactive",
        "interactive": interactive,
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://graph.facebook.com/v24.0/912195958636325/messages",
                headers=headers,
                json=payload,
            )

            if response.status_code != 200:
                print("❌ WhatsApp API Error:", response.text)
                return False

            return True

    except Exception as e:
        print("❌ WhatsApp send failed:", str(e))
        return False

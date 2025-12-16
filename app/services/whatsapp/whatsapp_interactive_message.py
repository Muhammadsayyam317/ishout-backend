import httpx
from app.config.credentials_config import config
from app.utils.helpers import format_followers


async def send_whatsapp_interactive_message(
    recipient_id: str,
    message_text: str,
    influencer: dict,
) -> bool:
    print("Entering send_whatsapp_interactive_message")
    access_token = config.META_WHATSAPP_ACCESSSTOKEN

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    username = influencer.get("username")
    followers = influencer.get("followers")
    country = influencer.get("country")
    pricing = influencer.get("pricing")
    pic = influencer.get("picture") or influencer.get("pic")

    if not username:
        print("⚠ Skipping influencer without username")
        return False

    message_body = (
        f"👤 @{username}\n"
        f"👥 Followers: {format_followers(followers)}\n"
        f"🌍 Country: {country or 'N/A'}\n"
        f"💰 Pricing: {pricing or 'N/A'}\n"
        f"🔗 https://www.instagram.com/{username}"
    )

    interactive = {
        "type": "button",
        "body": {"text": message_body},
        "footer": {"text": message_text},
        "action": {
            "buttons": [
                {
                    "type": "reply",
                    "reply": {
                        "id": f"approve_{influencer['_id']}",
                        "title": "Approve 👍",
                    },
                },
                {
                    "type": "reply",
                    "reply": {
                        "id": f"reject_{influencer['_id']}",
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

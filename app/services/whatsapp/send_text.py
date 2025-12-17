import httpx
from app.config.credentials_config import config


async def send_whatsapp_text_message(to: str, text: str):
    headers = {
        "Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(
            "https://graph.facebook.com/v24.0/912195958636325/messages",
            headers=headers,
            json=payload,
        )

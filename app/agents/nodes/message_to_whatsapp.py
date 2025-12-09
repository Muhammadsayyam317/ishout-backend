import httpx
from app.config.credentials_config import config


async def send_whatsapp_message(payload: dict) -> bool:

    headers = {
        "Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = await httpx.AsyncClient(timeout=15.0).post(
            "https://graph.facebook.com/v24.0/912195958636325/messages",
            headers=headers,
            json=payload,
        )

        return response.status_code == 200
    except httpx.RequestError:
        return False

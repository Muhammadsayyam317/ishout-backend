import httpx
from app.config.credentials_config import config
from app.core.exception import InternalServerErrorException


async def send_whatsapp_text_message(to: str, text: str):
    print("Entering into send_whatsapp_text_message")
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
    print(f"Payload: {payload}")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                f"https://graph.facebook.com/{config.WHATSAPP_GRAPH_API_VERSION}/{config.WHATSAPP_PHONE_NUMBER}/messages",
                headers=headers,
                json=payload,
            )
            if response.status_code != 200:
                raise InternalServerErrorException(
                    message=f"Error: {response.status_code}, {response.text}"
                )
        except Exception as e:
            print(f"Error sending message: {e}")
            raise InternalServerErrorException(
                message=f"Error sending message: {str(e)}"
            ) from e

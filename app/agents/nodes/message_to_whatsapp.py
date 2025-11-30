import logging
import httpx
from app.config.credentials_config import config


async def send_whatsapp_message(recipient_id: str, message_text: str) -> bool:
    headers = {
        "Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}",
        "Content-Type": "application/json",
    }

    message_payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message_text},
    }

    logging.info(f"Sending message to {recipient_id} with content: {message_payload}")
    try:
        response = await httpx.AsyncClient(timeout=10.0).post(
            "https://graph.facebook.com/v24.0/912195958636325/messages",
            headers=headers,
            json=message_payload,
        )
        logging.info(f"Response status code: {response.status_code}")

        if response.status_code != 200:
            logging.error(f"Error: {response.status_code}, {response.text}")
            return False
        return True
    except httpx.RequestError as http_error:
        logging.error(f"HTTP request error: {http_error}")
        return False
    except Exception as general_error:
        logging.error(f"Unexpected error: {general_error}")
        return False

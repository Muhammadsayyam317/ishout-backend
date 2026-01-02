import httpx
from fastapi import HTTPException
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

    print(f"Sending message to {recipient_id} with content: {message_payload}")
    try:
        print("Entering send_whatsapp_message")
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"https://graph.facebook.com/{config.WHATSAPP_GRAPH_API_VERSION}/{config.WHATSAPP_PHONE_NUMBER}/messages",
                headers=headers,
                json=message_payload,
            )
            print("Graph API Version: ", config.WHATSAPP_GRAPH_API_VERSION)
            print("Phone Number: ", config.WHATSAPP_PHONE_NUMBER)
            print(f"Response: {response}")
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Error: {response.status_code}, {response.text}",
            )
        return True
    except httpx.RequestError:
        return HTTPException(status_code=500, detail="HTTP request error")
    except Exception:
        return HTTPException(status_code=500, detail="Unexpected error")

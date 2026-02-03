from bson import ObjectId
import httpx
from app.config.credentials_config import config
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from app.utils.helpers import normalize_phone


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
                "https://graph.facebook.com/v22.0/967002123161751/messages",
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


async def send_message_from_ishout_to_user(text: str, user_id: str):
    print("Entering into send_message_from_ishout_to_user")
    print("--------------------------------")

    try:
        db = get_db()
        users_collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_USERS)
        user = await users_collection.find_one({"_id": ObjectId(user_id)})

        phone = user.get("phone")
        if not phone:
            raise InternalServerErrorException(message="User phone number not found")
        to = normalize_phone(phone)
        headers = {
            "Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}",
            "Content-Type": "application/json",
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": text,
            },
        }

        print("Using PHONE_NUMBER_ID:", config.WHATSAPP_PHONE_NUMBER)
        print("Payload:", payload)
        print("--------------------------------")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://graph.facebook.com/v22.0/967002123161751/messages",
                headers=headers,
                json=payload,
            )

        print("Status:", response.status_code)
        print("Response:", response.text)

        if response.status_code != 200:
            print("WhatsApp API error:", response.text)

    except Exception as e:
        print("Error sending message from ishout to user")
        print("--------------------------------")
        print(e)
        print("--------------------------------")
        return

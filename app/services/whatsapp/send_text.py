from bson import ObjectId
import httpx
from app.config.credentials_config import config
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from app.utils.Enums.user_enum import SenderType
from app.utils.helpers import normalize_phone
from app.utils.printcolors import Colors


async def send_whatsapp_text_message(to: str, text: str):
    print(f"{Colors.GREEN}Entering into send_whatsapp_text_message")
    print("--------------------------------")
    headers = {
        "Authorization": f"Bearer {config.META_WHATSAPP_ACCESSSTOKEN}",
        "Content-Type": "application/json",
    }
    print("Entering into send_whatsapp_text_message")
    print("--------------------------------")
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
            print("Response: ", response.json())
            if response.status_code != 200:
                raise InternalServerErrorException(
                    message=f"Error: {response.status_code}, {response.text}"
                )
        except Exception as e:
            print(f"Error sending message: {e}")
            raise InternalServerErrorException(
                message=f"Error sending message: {str(e)}"
            ) from e


async def send_message_from_ishout_to_user(text: str, user_id: str, sender: SenderType):
    print(f"{Colors.GREEN}Entering into send_message_from_ishout_to_user")
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

        print(f"{Colors.CYAN}Using PHONE_NUMBER_ID: {config.WHATSAPP_PHONE_NUMBER}")
        print(f"{Colors.CYAN}Payload: {payload}")
        print("--------------------------------")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://graph.facebook.com/v22.0/967002123161751/messages",
                headers=headers,
                json=payload,
            )

        print(f"{Colors.CYAN}Status: {response.status_code}")
        print(f"{Colors.CYAN}Response: {response.text}")
        print("--------------------------------")
        print(f"{Colors.YELLOW}Exiting from send_message_from_ishout_to_user")

        if response.status_code != 200:
            print(f"{Colors.RED}WhatsApp API error: {response.text}")
            print("--------------------------------")

    except Exception as e:
        print(f"{Colors.RED}Error sending message from ishout to user: {e}")
        print("--------------------------------")
        print(e)
        print("--------------------------------")
        return

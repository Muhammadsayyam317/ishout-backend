import httpx
from app.config import config
from app.core.exception import InternalServerErrorException


async def Send_Insta_Message(message: str, recipient_id: str):
    print(f"Sending message to {recipient_id}: {message}")
    if not message:
        return None
    try:
        PAGE_ACCESS_TOKEN = config.PAGE_ACCESS_TOKEN
        backend_url = (
            f"https://graph.facebook.com/{config.IG_GRAPH_API_VERSION}/me/messages"
        )
        print(f"backend_url: {backend_url}")
        headers = {
            "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {"recipient": {"id": recipient_id}, "message": {"text": message}}
        print(f"payload: {payload}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(backend_url, json=payload, headers=headers)
            print(f"response: {response.text}")
            if response.status_code != 200:
                raise InternalServerErrorException(
                    message=f"Error sending message: {response.text}"
                )
            print(f"Message sent to {recipient_id}: {message}")
            print("Message sent successfully")
            return True
    except Exception as e:
        print(f"Error sending message: {e}")
        raise InternalServerErrorException(message=str(e)) from e

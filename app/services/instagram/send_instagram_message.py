import httpx
from app.config import config
from app.core.exception import InternalServerErrorException


async def Send_Insta_Message(message: str, psid: str):
    print(f"Sending message to {psid}: {message}")
    if not message:
        return None
    try:
        PAGE_ACCESS_TOKEN = config.PAGE_ACCESS_TOKEN
        print(f"PAGE_ACCESS_TOKEN: {PAGE_ACCESS_TOKEN}")
        backend_url = (
            f"https://graph.facebook.com/{config.IG_GRAPH_API_VERSION}/me/messages"
        )
        print(f"backend_url: {backend_url}")
        headers = {
            "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {"recipient": {"id": psid}, "message": {"text": message}}
        print(f"payload: {payload}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(backend_url, json=payload, headers=headers)
            print(f"response: {response.text}")
            if response.status_code != 200:
                raise InternalServerErrorException(
                    message=f"Error sending message: {response.text}"
                )
            return True
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e

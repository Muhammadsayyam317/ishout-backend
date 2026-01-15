import time
import httpx
from app.Schemas.instagram.message_schema import InstagramMessage
from app.config import config
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db
from datetime import datetime, timezone
from fastapi import BackgroundTasks

from app.model.Instagram.instagram_message import InstagramMessageModel


async def Send_Insta_Message(
    message: str, recipient_id: str, background_tasks: BackgroundTasks
):
    print(f"Sending message to {recipient_id}: {message}")
    if not message:
        raise InternalServerErrorException(message="Message is required")
    try:
        PAGE_ACCESS_TOKEN = config.PAGE_ACCESS_TOKEN
        backend_url = (
            f"https://graph.facebook.com/{config.IG_GRAPH_API_VERSION}/me/messages"
        )
        headers = {
            "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {"recipient": {"id": recipient_id}, "message": {"text": message}}
        print(f"Sending message to {recipient_id}: {message}")
        print(f"POST URL: {backend_url}")
        print(f"Payload: {payload}")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(backend_url, json=payload, headers=headers)
            print(f"IG DM response: {response.text}")
            if response.status_code != 200:
                raise InternalServerErrorException(
                    message=f"Error sending message: {response.status_code}, {response.text}"
                )
            print(f"Message sent Successfully to {recipient_id}: {message}")
            print("Exiting from Send_Insta_Message")
            return True
    except Exception as e:
        print(f"Error sending message: {e}")
        raise InternalServerErrorException(message=str(e)) from e


# async def save_instagram_reply_message(thread_id: str, message: str):
#     print(f"Saving message to {thread_id}: {message}")
#     if not message:
#         raise InternalServerErrorException(message="Message is required")
#     try:
#         payload = {
#             "thread_id": thread_id,
#             "sender_type": "AI",
#             "platform": "INSTAGRAM",
#             "username": "iShout",
#             "message": message,
#             "timestamp": time.time(),
#             "attachments": [],
#         }
#         await InstagramMessageModel.create(payload)
#         print(f"Message saved successfully to {thread_id}: {message}")
#         return True
#     except Exception as e:
#         raise InternalServerErrorException(message=str(e)) from e


# async def save_Instagram_Received_Message(payload: dict):
#     print(f"Saving received message: {payload}")
#     if not payload:
#         raise InternalServerErrorException(message="Payload is required")
#     try:
#         await InstagramMessageModel.create(payload)
#         return payload
#     except Exception as e:
#         print(f"Error saving received message: {e}")
#         raise InternalServerErrorException(message=str(e)) from e

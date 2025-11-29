from fastapi import Request
import logging
import httpx
from app.config.credentials_config import config
from fastapi import Response
from app.services.llm_router import Query_to_llm
from app.services.message_classification import message_classification
from app.utils.message_type import identify_message_type


async def handle_whatsapp_events(request: Request) -> Response:
    try:
        payload = await request.json()
        message = await identify_message_type(
            payload["entry"][0]["changes"][0]["value"]
        )
        if message["message_type"] == "text":
            filter_message = await message_classification(message["message_text"])
        if filter_message.intent == "find_influencers":
            request_influencer = await Query_to_llm(filter_message.result)
            response_status = await send_whatsapp_message(
                message["sender_id"], request_influencer
            )
            if response_status:
                return Response(content=request_influencer, status_code=200)
            else:
                return Response(content="Failed to send message", status_code=500)
        return Response(content=response_status, status_code=200)
    except Exception as e:
        logging.error(f"Error handling WhatsApp events: {e}")
        return Response(content="Internal server error", status_code=500)


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
            f"https://graph.facebook.com/v{config.VERSION}/{config.PHONE_NUMBER_ID}/messages",
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

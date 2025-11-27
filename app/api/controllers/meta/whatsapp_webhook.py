from fastapi import Request
import logging
import httpx
from fastapi import Response
from app.config import config

# from app.config.llm_router import llm_router


async def verify_whatsapp_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == config.META_VERIFY_TOKEN:
        return Response(content=challenge, status_code=200)
    return Response(status_code=403)


async def handle_whatsapp_events(request: Request) -> Response:
    try:
        logging.info("Processing incoming event...")
        payload = await request.json()
        event_data = payload["entry"][0]["changes"][0]["value"]
        logging.info(f"Event data: {event_data}")

        if "messages" in event_data:
            logging.info(f"📩 Incoming Message: {event_data['messages'][0]}")
            user_message = event_data["messages"][0]
            sender_id = user_message["from"]
            # message_content = user_message["text"]["body"]

            # bot_reply = llm_router(message_content)
            bot_reply = "Hello, how can I help you today?"
            response_status = await send_whatsapp_message(sender_id, bot_reply)

            if response_status:
                return {"status": "success", "message": "Processed"}
            else:
                return Response(content="Failed to send response", status_code=500)
        elif "statuses" in event_data:
            logging.info(
                f"📊 Status Update: {event_data['statuses'][0]['status']} (ID: {event_data['statuses'][0]['id']})"
            )
            return Response(content="Status update received", status_code=200)

        else:
            return Response(content="Unknown event type", status_code=400)

    except Exception as error:
        logging.error(f"Error handling event: {error}", exc_info=True)
        return Response(content="Internal server error", status_code=500)


async def send_whatsapp_message(recipient_id: str, message_text: str) -> bool:
    """
    Sends a response message to a user via the WhatsApp Cloud API.

    Args:
        from_number (str): The recipient's phone number.
        response_text (str): The message content to be sent.
        message_type (str, optional): The type of message (default is "text").

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    headers = {
        "Authorization": "Bearer " + config.META_WHATSAPP_ACCESSSTOKEN,
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
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://graph.facebook.com/{config.VERSION}/{config.PHONE_NUMBER_ID}/messages",
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

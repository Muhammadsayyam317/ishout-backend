from fastapi import Request
import logging
import httpx
from fastapi import Response
from app.config import config, llm_router
from app.utils.clients import get_openai_client

client = get_openai_client()


async def verify_whatsapp_webhook(request: Request):
    params = request.query_params
    if "hub.mode" not in params:
        return Response(content="WhatsApp Webhook is active", status_code=200)

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
            messages = event_data["messages"]
            if not messages or len(messages) == 0:
                logging.warning("No messages found in event data")
                return Response(content="No messages to process", status_code=200)

            user_message = messages[0]
            sender_id = user_message.get("from")

            if not sender_id:
                logging.warning("No sender ID found in message")
                return Response(content="No sender ID", status_code=200)

            logging.info(f"Incoming Message FROM: {sender_id}")

            # Handle different message types
            message_text = None

            # Check if message has text directly
            if "text" in user_message:
                message_text = (
                    user_message["text"].get("body")
                    if isinstance(user_message["text"], dict)
                    else user_message["text"]
                )
            # Check if message is nested under "message" key
            elif "message" in user_message:
                if "text" in user_message["message"]:
                    message_text = (
                        user_message["message"]["text"].get("body")
                        if isinstance(user_message["message"]["text"], dict)
                        else user_message["message"]["text"]
                    )
            # Check if type is text and text is at root level
            elif user_message.get("type") == "text":
                message_text = (
                    user_message.get("text", {}).get("body")
                    if isinstance(user_message.get("text"), dict)
                    else user_message.get("text")
                )

            # Handle non-text messages
            if not message_text:
                message_type = user_message.get("type", "unknown")
                logging.info(
                    f"User {sender_id} sent non-text message type: {message_type}"
                )
                # Send a helpful message for non-text messages
                bot_reply = "I can only process text messages. Please send me a text message to find influencers. For example: 'Find 10 beauty influencers on Instagram'"
                response_status = await send_whatsapp_message(sender_id, bot_reply)
                if response_status:
                    return {
                        "status": "success",
                        "message": "Processed non-text message",
                    }
                return Response(content="Failed to send response", status_code=500)

            # Log user number and message
            logging.info(f"User Number: {sender_id} | Message: {message_text}")

            # Process text message
            bot_reply = await llm_router(message_text, sender_id)
            response_status = await send_whatsapp_message(sender_id, bot_reply)

            if response_status:
                return {"status": "success", "message": "Processed"}
            else:
                return Response(content="Failed to send response", status_code=500)
        elif "statuses" in event_data:
            logging.info(
                f"Status Update: {event_data['statuses'][0]['status']} (ID: {event_data['statuses'][0]['id']})"
            )
            return Response(content="Status update received", status_code=200)

        else:
            return Response(content="Unknown event type", status_code=400)

    except Exception as error:
        logging.error(f"Error handling event: {error}", exc_info=True)
        return Response(content="Internal server error", status_code=500)


async def send_whatsapp_message(recipient_id: str, message_text: str) -> bool:
    headers = {
        "Authorization": "Bearer "
        + "EAAVTqVZBPnhYBQPpws4RTBzBGtxZARiAecMVFFvkftKgzRjjTCRkYMYqZBMuIg9pfCLy8ty9cp4JLnw4LKkKZAeqINE2tfz0glk4IgtTxt32dVDFQIAiHGm4JZAzKr4InGMoalsd5T0xFflZAgsYO5N4MOnz0g6vN7UvoZANHdyOEgNkoOXZC4FZAOXsH4WYK2is4VIDT",
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

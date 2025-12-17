from fastapi import Request
import logging
import httpx
from app.config.credentials_config import config
from fastapi import Response
from app.agents.nodes.query_llm import Query_to_llm
from app.agents.nodes.message_classification import message_classification
from app.agents.nodes.message_type import identify_message_type


async def instagramagent(request: Request) -> Response:
    """
    Orchestrator function for handling WhatsApp events:
    1. Identifies message type
    2. Classifies message intent
    3. Routes to LLM if related to finding influencers
    4. Sends reply back to WhatsApp
    """
    try:
        payload = await request.json()
        event_data = payload["entry"][0]["changes"][0]["value"]

        event_type = (
            "message"
            if "messages" in event_data
            else "status" if "statuses" in event_data else "unknown"
        )
        logging.info(f"Received Instagram webhook event type: {event_type}")

        # Step 1: Identify message type
        message_data = await identify_message_type(event_data)
        sender_id = message_data.get("sender_id")
        message_text = message_data.get("message_text")
        message_type = message_data.get("message_type")

        # Handle non-message events (status updates, etc.) - return 200 OK
        if not sender_id:
            logging.info(
                "No sender_id found - likely a status update or non-message event, skipping processing"
            )
            return Response(
                content="Event received (non-message event)", status_code=200
            )

        # Step 2: Handle non-text messages
        if message_type != "text" or not message_text:
            bot_reply = "I can only process text messages. Please send me a text message to find influencers."
            response_status = await send_whatsapp_message(sender_id, bot_reply)
            if response_status:
                return Response(content="Non-text message handled", status_code=200)
            else:
                return Response(content="Failed to send response", status_code=500)

        # Step 3: Classify message intent
        filter_message = await message_classification(message_text)
        logging.info(f"Message classified with intent: {filter_message.intent}")

        # Step 4: Route based on intent
        if filter_message.intent == "find_influencers":
            # Step 5: Send query to LLM
            llm_response = await Query_to_llm(message_text)
            # Step 6: Send reply back to WhatsApp
            response_status = await send_whatsapp_message(sender_id, llm_response)
            if response_status:
                return Response(
                    content="Message processed successfully", status_code=200
                )
            else:
                return Response(content="Failed to send message", status_code=500)
        else:
            # Handle other intents
            bot_reply = "I'm here to help you find influencers. Could you please tell me what kind of influencers you're looking for? For example: 'Find 10 beauty influencers on Instagram' or 'Show me fitness influencers on TikTok'."
            response_status = await send_whatsapp_message(sender_id, bot_reply)
            if response_status:
                return Response(
                    content="Response sent for non-influencer query", status_code=200
                )
            else:
                return Response(content="Failed to send message", status_code=500)

    except Exception as e:
        logging.error(f"Error handling WhatsApp events: {e}", exc_info=True)
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

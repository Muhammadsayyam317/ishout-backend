from fastapi import Request
import logging
from app.agents.nodes.message_classification import message_classification
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from fastapi import Response

# from typing import TypeDict
from app.agents.nodes.message_type import identify_message_type
from app.agents.nodes.query_llm import Query_to_llm

# from langgraph.graph import StateGraph, END


# class ConversationState(TypeDict):
#     message: str


async def handle_whatsapp_events(request: Request) -> Response:
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

        # Log the event type for debugging
        event_type = (
            "message"
            if "messages" in event_data
            else "status" if "statuses" in event_data else "unknown"
        )
        logging.info(f"Received WhatsApp webhook event type: {event_type}")

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

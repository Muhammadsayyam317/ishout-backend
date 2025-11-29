import logging
from typing import Optional, Dict, Any


async def identify_message_type(event_data: Dict[str, Any]) -> Dict[str, Optional[str]]:
    try:
        if "messages" not in event_data:
            logging.warning("No messages found in event data")
            return {"sender_id": None, "message_text": None, "message_type": None}

        user_message = event_data["messages"][0]
        sender_id = user_message.get("from")
        message_type = user_message.get("type", "unknown")
        message_text = None

        # Extract text from text messages
        if message_type == "text":
            if "text" in user_message:
                text_data = user_message["text"]
                if isinstance(text_data, dict):
                    message_text = text_data.get("body")
                else:
                    message_text = text_data
            else:
                message_text = user_message.get("text")

        return {
            "sender_id": sender_id,
            "message_text": message_text,
            "message_type": message_type,
        }

    except Exception as e:
        logging.error(f"Error identifying message type: {e}", exc_info=True)
        return {"sender_id": None, "message_text": None, "message_type": None}

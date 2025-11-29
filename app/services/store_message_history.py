import logging
import uuid
from datetime import datetime
from typing import List, Tuple, Optional
from app.db.connection import get_db


def save_interaction_to_db(
    question: Optional[str] = None,
    response: Optional[str] = None,
    sender_id: Optional[str] = None,
) -> List[Tuple[str, str]]:
    """
    Save interaction to DB or retrieve previous interactions.
    If question and response are provided, saves the interaction.
    If only sender_id is provided, returns previous interactions for that sender.
    Returns list of (question, response) tuples.
    """
    try:
        logging.info("Get the database session.")
        db = get_db()
        collection = db.get_collection("whatsapp")

        # If saving an interaction
        if question is not None and response is not None:
            interaction_id = str(uuid.uuid4())
            interaction_data = {
                "id": interaction_id,
                "question": question,
                "response": response,
                "interaction_time": datetime.now(),
            }
            if sender_id:
                interaction_data["sender_id"] = sender_id

            collection.insert_one(interaction_data)
            logging.info("User interaction saved successfully.")
            return []

        # If retrieving interactions
        query = {}
        if sender_id:
            query["sender_id"] = sender_id

        # Get last 5 interactions, sorted by time descending
        interactions = collection.find(query).sort("interaction_time", -1).limit(5)
        result = [
            (interaction.get("question", ""), interaction.get("response", ""))
            for interaction in interactions
        ]
        # Reverse to get chronological order (oldest first)
        return list(reversed(result))

    except Exception as error:
        logging.error(f"Error in save_interaction_to_db: {error}")
        return []


def is_first_message(sender_id: str) -> bool:
    """Check if this is the first message from a sender"""
    try:
        db = get_db()
        collection = db.get_collection("whatsapp")
        count = collection.count_documents({"sender_id": sender_id})
        return count == 0
    except Exception as error:
        logging.error(f"Error checking first message: {error}")
        return True  # Default to True if error occurs

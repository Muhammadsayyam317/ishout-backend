import logging
from typing import Any, Tuple
from langfuse import observe
from app.config.credentials_config import config
from app.config.store_message_history import save_interaction_to_db, is_first_message
from app.utils.clients import get_openai_client
from app.models.message_model import MessageRequestType


@observe()
async def route_message_request(
    user_input: str,
    sender_id: str = None,
    client: Any = get_openai_client(),
    model_name: str = config.OPENAI_MODEL_NAME,
) -> Tuple[MessageRequestType, bool]:
    """
    Route message request and return classification along with is_first_message flag.
    Returns: (MessageRequestType, is_first_message)
    """
    logging.info("Routing message request with memory")

    # Check if this is the first message
    first_message = False
    if sender_id:
        first_message = is_first_message(sender_id)

    # Get previous interactions for this sender
    interactions = save_interaction_to_db(sender_id=sender_id) if sender_id else []

    messages = [
        {
            "role": "system",
            "content": "Determine if this is a request to find influencers. Return 'find_influencers' if the user wants to find influencers, otherwise return a different classification.",
        },
    ]

    # Add conversation history if available
    if interactions:
        messages.append(
            {
                "role": "system",
                "content": "These are the last five messages of previous conversation but you do not need to use these pieces of information if not relevant:\n"
                + "\n".join(
                    [
                        f"User: {interaction[0]}\nAssistant: {interaction[1]}"
                        for interaction in interactions
                    ]
                )
                + "\n\n(End of previous conversation)",
            }
        )

    messages.append({"role": "user", "content": f"Current conversation: {user_input}"})

    logging.info("Calling the LLM...")
    completion = client.beta.chat.completions.parse(
        model=model_name,
        messages=messages,
        response_format=MessageRequestType,
    )

    result = completion.choices[0].message.parsed
    logging.info(
        f"Request routed as: {result.request_type} with confidence: {result.confidence_score}"
    )

    # Save interaction if sender_id is provided
    if sender_id:
        save_interaction_to_db(user_input, result.request_type, sender_id)

    return result, first_message

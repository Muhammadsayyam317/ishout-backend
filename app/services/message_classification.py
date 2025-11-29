import logging
from typing import Any, Tuple
from langfuse import observe
from app.config.credentials_config import config
from app.services.store_message_history import save_interaction_to_db, is_first_message
from app.utils.clients import get_openai_client
from app.models.message_model import MessageRequestType


@observe()
async def route_message_request(
    user_input: str,
    sender_id: str = None,
    client: Any = get_openai_client(),
    model_name: str = config.OPENAI_MODEL_NAME,
) -> Tuple[MessageRequestType, bool]:

    if sender_id:
        first_message = is_first_message(sender_id)

    messages = [
        {
            "role": "system",
            "content": "Determine if this is a request to find influencers. Return 'find_influencers' if the user wants to find influencers, otherwise return i am here to provide you information about influencers. For example: 'I am here to provide you information about influencers. For example: 'Find 10 beauty influencers on Instagram' or 'Show me fitness influencers on TikTok'.",
        },
    ]

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
    # if sender_id:
    #     save_interaction_to_db(user_input, result.request_type, sender_id)

    return result, first_message

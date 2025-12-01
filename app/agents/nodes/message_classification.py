import logging
from langfuse import observe
from app.config.credentials_config import config
from app.utils.clients import get_openai_client
from app.models.message_model import MessageRequestType


@observe()
async def message_classification(
    user_input: str,
) -> MessageRequestType:
    try:

        client = get_openai_client()
        intent = client.chat.completions.parse(
            model=config.OPENAI_MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Classify the user's message into one of these intents:\n"
                        "- 'greet' if the user is just greeting or saying hi/hello/hey.\n"
                        "- 'find_influencers' if the user is asking to find influencers "
                        "for a campaign (e.g. 'Find 4 fashion influencers on Instagram in UAE').\n"
                        "- 'other' for anything else.\n\n"
                        "Do NOT ask the user questions yourself or mention missing fields. "
                        "Just classify the intent and (optionally) provide a short description "
                        "of the user's request."
                    ),
                },
                {"role": "user", "content": user_input},
            ],
            response_format=MessageRequestType,
        )

        result = intent.choices[0].message.parsed
        logging.info(f"Request routed as: {result.intent}")
        return result
    except Exception as e:
        logging.error(f"Error classifying message: {e}")
        return MessageRequestType(intent="other")

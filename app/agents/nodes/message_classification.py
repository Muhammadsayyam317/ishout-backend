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
                    "content": "Classify intent: find_influencers or other if the user is asking about influencers, otherwise return other if the user is asking about something else like how to use the bot, etc. For example: 'Find 10 beauty influencers on Instagram' or 'Show me fitness influencers on TikTok' is a find_influencers request, 'How to use the bot' is an other request.also make sure the platform,category,country ,number of influencers,and budget is specified if not specified then ask from user about these feild and oncer user provide these feild these move further ,otherwise mention the user the missing feilds in response ",
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

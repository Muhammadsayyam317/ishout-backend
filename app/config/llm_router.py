# Main handler
import logging
from app.api.controllers.influencers_controller import find_influencers_by_campaign
from app.models.influencers_model import FindInfluencerRequest
from app.config.message_classification import route_message_request


async def llm_router(user_message):
    """
    Handles user requests by classifying the intent and routing it
    to the appropriate function.

    Args:
        user_message (str): The message sent by the user.

    Returns:
        str: Response from the appropriate function or an error message.
    """
    try:
        # Step 1: Classify the user's intent
        classify_message = await route_message_request(user_message)
        intent = classify_message.request_type

        # Step 2: Route the request based on the classified intent
        if intent == "find_influencers":
            return await find_influencers_by_campaign(
                FindInfluencerRequest(
                    campaign_id=user_message.campaign_id,
                    user_id=user_message.user_id,
                    limit=user_message.limit,
                )
            )

        else:
            return "I'm unable to process that request. Can you provide more details?"

    except Exception as e:
        # Log the error and return a user-friendly response
        logging.error(f"Error handling request: {e}")
        return (
            "An error occurred while processing your request. Please try again later."
        )


# question1 = "What should I do if my package is lost?"
# print(llm_router(question1))
# question2 = "How long does it take to send a package to Economy International? And the price?"
# print(llm_router(question2))
# question3 = "I want to track the location of my package"
# print(llm_router(question3))

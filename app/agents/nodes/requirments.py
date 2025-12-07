import json
import logging
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message
from app.agents.nodes.state import update_user_state
from app.models.whatsappconversation_model import ConversationState
from app.services.campaign_service import create_whatsapp_campaign
from app.utils.extract_feilds import (
    extract_followers,
    extract_platforms,
    extract_limit,
    extract_countries,
    extract_categories,
)


async def node_debug_before(state):
    logging.info("\n\n===== DEBUG BEFORE =====\n" + json.dumps(state, indent=2))
    return state


async def node_debug_after(state):
    logging.info("\n\n===== DEBUG AFTER =====\n" + json.dumps(state, indent=2))
    return state


async def node_requirements(state):
    msg = state.get("user_message", "").lower()

    # ----------------------------------------
    # STEP 1: ASK PLATFORM
    # ----------------------------------------
    if state["step"] == "platform":
        platforms = extract_platforms(msg)
        if platforms:
            state["platform"] = platforms
            state["step"] = "category"
            state["reply"] = (
                "Great! Now tell me the *category* of influencers.\n"
                "Example: beauty, fashion, tech"
            )
        else:
            state["reply"] = (
                "Which platform do you want influencers from?\n"
                "Instagram, TikTok, or YouTube?"
            )
        return state

    # ----------------------------------------
    # STEP 2: ASK CATEGORY
    # ----------------------------------------
    if state["step"] == "category":
        categories = extract_categories(msg)
        if categories:
            state["category"] = categories
            state["step"] = "country"
            state["reply"] = (
                "Nice! Now tell me the *country*.\n"
                "Example: UAE, Saudi Arabia, Kuwait"
            )
        else:
            state["reply"] = (
                "Please tell me the category.\n"
                "Example: fashion, beauty, food, fitness"
            )
        return state

    # ----------------------------------------
    # STEP 3: ASK COUNTRY
    # ----------------------------------------
    if state["step"] == "country":
        countries = extract_countries(msg)
        if countries:
            state["country"] = countries
            state["step"] = "followers"
            state["reply"] = (
                "Good! What *follower range* are you looking for?\n"
                "Example: 10k-50k, 50k-200k"
            )
        else:
            state["reply"] = (
                "Please tell me the country.\n" "Example: UAE, Saudi Arabia"
            )
        return state

    # ----------------------------------------
    # STEP 4: ASK FOLLOWERS
    # ----------------------------------------
    if state["step"] == "followers":
        followers = extract_followers(msg)
        if followers:
            state["followers"] = followers
            state["step"] = "limit"
            state["reply"] = (
                "Perfect! How many influencers do you want?\n" "Example: 5, 10, 15"
            )
        else:
            state["reply"] = "Please enter follower range.\n" "Example: 10k-50k"
        return state

    # ----------------------------------------
    # STEP 5: ASK LIMIT
    # ----------------------------------------
    if state["step"] == "limit":
        limit = extract_limit(msg)
        if limit:
            state["limit"] = limit
            state["step"] = "confirm"

            # Show summary
            state["reply"] = (
                "**Please confirm your campaign details:**\n\n"
                f"• Platform: {', '.join(state['platform'])}\n"
                f"• Category: {', '.join(state['category'])}\n"
                f"• Country: {', '.join(state['country'])}\n"
                f"• Followers: {', '.join(state['followers'])}\n"
                f"• Influencers Required: {state['limit']}\n\n"
                "Reply *YES* to create your campaign or *NO* to restart."
            )
        else:
            state["reply"] = "Please tell me how many influencers you need."
        return state

    # ----------------------------------------
    # STEP 6: CONFIRMATION
    # ----------------------------------------
    if state["step"] == "confirm":
        if "yes" in msg:
            state["step"] = "creating"
            state["done"] = True
            state["reply"] = None
            return state
        elif "no" in msg:
            # Reset flow
            state.update(
                {
                    "step": "platform",
                    "platform": [],
                    "category": [],
                    "country": [],
                    "followers": [],
                    "limit": None,
                }
            )
            state["reply"] = (
                "Okay, let's start again.\n\n"
                "Which platform do you want influencers from?"
            )
            return state
        else:
            state["reply"] = "Please reply YES to confirm or NO to restart."
            return state

    return state


async def node_ask_user(state, config):
    sender = state.get("sender_id") or config["configurable"]["thread_id"]
    if state.get("reply") and not state.get("reply_sent"):
        await send_whatsapp_message(sender, state["reply"])
        state["reply_sent"] = True
        await update_user_state(sender, state)
    return state


async def node_create_campaign(state: ConversationState):
    try:
        logging.info("📌 Creating WhatsApp Campaign with state:")
        logging.info(json.dumps(state, indent=2, default=str))

        required = ["platform", "country", "category", "limit", "followers"]
        missing = [key for key in required if not state.get(key)]

        if missing:
            state["reply"] = (
                f"Missing required fields to create campaign: {', '.join(missing)}"
            )
            state["campaign_created"] = False
            return state
        result = await create_whatsapp_campaign(state)
        if not result or "campaign_id" not in result:
            state["reply"] = "Failed to create campaign. Please try again."
            state["campaign_created"] = False
            return state

        state["campaign_id"] = result["campaign_id"]
        state["campaign_created"] = True
        state["reply"] = None

        logging.info(f"🎉 Campaign created successfully: {result['campaign_id']}")

        return state

    except Exception as e:
        logging.error(f"❌ Error creating WhatsApp campaign: {str(e)}")

        state["reply"] = "Something went wrong while creating the campaign."
        state["campaign_created"] = False
        return state


async def node_acknowledge_user(state: ConversationState, config):
    sender = state.get("sender_id") or config["configurable"]["thread_id"]
    final_msg = (
        "Great! I got all your campaign details.\n"
        "iShout admin team will review them and we’ll notify you once it's approved.\n"
        "Thank you for using iShout! 🎉"
    )
    await send_whatsapp_message(sender, final_msg)
    state["done"] = True
    state["reply_sent"] = True
    return state


def missing_fields(state: ConversationState):
    missing = []
    for field in [
        "platform",
        "country",
        "limit",
        "category",
        "followers",
    ]:
        value = state.get(field)
        if field == "limit":
            is_missing = value is None or (isinstance(value, int) and value <= 0)
        else:
            if isinstance(value, list):
                is_missing = len(value) == 0
            else:
                is_missing = value is None or value == []
        if is_missing:
            missing.append(field)
    return missing

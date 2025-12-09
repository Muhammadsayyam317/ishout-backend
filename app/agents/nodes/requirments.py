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
    print("➡ Entered node_requirements")
    msg = state.get("user_message", "")

    new_platforms = extract_platforms(msg)
    limit = extract_limit(msg)
    new_countries = extract_countries(msg)
    new_categories = extract_categories(msg)
    new_followers = extract_followers(msg)

    info_updated = False

    if new_platforms:
        state["platform"] = new_platforms
        info_updated = True

    if limit is not None:
        state["limit"] = limit
        info_updated = True

    if new_countries:
        state["country"] = new_countries
        info_updated = True

    if new_categories:
        state["category"] = new_categories
        info_updated = True

    if new_followers:
        state["followers"] = new_followers
        info_updated = True

    if info_updated:
        state["reply_sent"] = False

    missing = missing_fields(state)
    if "platform" in missing:
        state["reply"] = (
            "👋 Welcome to iShout!\n\n"
            "Let's find the perfect influencers for your campaign 🎲\n\n"
            "Which social media platform are you targeting?\n\n"
            "📱 Examples: Instagram, TikTok, YouTube"
        )
        return state
    if "category" in missing:
        state["reply"] = (
            f"✅ Great! *{', '.join(state['platform'])}* it is!\n\n"
            "Now, what category or niche are you looking for?\n\n"
            "💡 Examples: Fashion, Beauty, Tech, Fitness, Food, Travel, Gaming"
        )
        return state
    if "country" in missing:
        state["reply"] = (
            f"✅ Perfect! *{', '.join(state['category'])}* influencers coming up!\n\n"
            "Which country or region should these influencers be based in?\n\n"
            "🌍 Examples: UAE, Kuwait, Saudi Arabia, Egypt, Qatar"
        )
        return state
    if "limit" in missing:
        state["reply"] = (
            f"✅ Got it! Looking for influencers in *{', '.join(state['country'])}*\n\n"
            "How many influencers would you like to connect with?\n\n"
            "🔢 Examples: 5, 10, 20, 50"
        )
        return state
    if "followers" in missing:
        state["reply"] = (
            f"✅ Noted! We'll find *{state.get('limit')}* influencers for you.\n\n"
            "What follower range are you targeting?\n\n"
            "👥 Examples:\n"
            "• 5k-10k (Micro influencers)\n"
            "• 200k (Mid-tier)\n"
            "• 500k+ (Macro influencers)\n"
            "• 1M+ (Mega influencers)"
        )
        return state

    state["reply"] = None
    state["ready_for_campaign"] = True
    print(f"➡ Exited node_requirements: {state}")
    return state


async def node_ask_user(state, config):
    print(f"➡ Entered node_ask_user: {state}")
    sender = state.get("sender_id") or config["configurable"]["thread_id"]
    if state.get("reply") and not state.get("reply_sent"):
        await send_whatsapp_message(sender, state["reply"])
        state["reply_sent"] = True
        await update_user_state(sender, state)
    print(f"➡ Exited node_ask_user: {state}")
    return state


async def node_create_campaign(state: ConversationState):
    print("➡ Entered node_create_campaign")
    result = await create_whatsapp_campaign(state)
    state["campaign_id"] = result["campaign_id"]
    state["campaign_created"] = True
    state["reply"] = None
    print(f"➡ Exited node_create_campaign: {state}")
    return state


async def node_acknowledge_user(state: ConversationState, config):
    print("➡ Entered node_acknowledge_user")
    sender = state.get("sender_id") or config["configurable"]["thread_id"]

    if not state.get("acknowledged"):
        Acknowledgement_message = (
            "🎉 *Campaign Created Successfully!*\n\n"
            "Here's a summary of your campaign:\n\n"
            "📱 *Platform:* " + ", ".join(state["platform"]) + "\n"
            "🎯 *Category:* " + ", ".join(state["category"]) + "\n"
            "🌍 *Location:* " + ", ".join(state["country"]) + "\n"
            "👥 *Followers:* " + ", ".join(state["followers"]) + "\n"
            "🔢 *Number of Influencers:* " + str(state["limit"]) + "\n\n"
            "✨ Perfect iShout will shortlist matching influencers.\n\n"
            "We'll notify you once we have curated the perfect influencers for you!\n\n"
            "Thank you for choosing iShout!🎉"
        )
        await send_whatsapp_message(sender, Acknowledgement_message)
        state["acknowledged"] = True

    state["done"] = True
    print("➡ Campaign acknowledged, state marked as done")
    return state


def missing_fields(state: ConversationState):
    missing = []
    for field in ["platform", "category", "country", "limit", "followers"]:
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

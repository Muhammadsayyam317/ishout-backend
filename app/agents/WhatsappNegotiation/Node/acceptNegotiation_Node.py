from app.Schemas.instagram.negotiation_schema import NextAction
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.printcolors import Colors
from app.db.connection import get_db
from bson import ObjectId


async def accept_negotiation_node(state: WhatsappNegotiationState):
    print(f"{Colors.GREEN}Entering accept_negotiation_node")
    print("--------------------------------")

    state["negotiation_status"] = "agreed"
    state["negotiation_completed"] = True
    # Mark the conversation as handed over / completed for dashboard purposes.
    state["conversation_mode"] = "HUMAN_TAKEOVER"
    state["human_takeover"] = True
    # Pause the negotiation agent so further messages don't re-trigger the flow.
    state["agent_paused"] = True

    final_price = state.get("last_offered_price")
    if final_price is None:
        final_price_text = ""
    else:
        final_price_text = f" at ${final_price:.2f}"

    # If we have a campaign brief, append a structured summary to the acceptance message.
    campaign_brief = state.get("campaign_brief") or {}
    brand_overview = campaign_brief.get("brand_name_influencer_campaign_brief")
    deliverables = campaign_brief.get("deliverables_per_influencer") or []
    timeline = campaign_brief.get("timeline") or []
    hashtags = campaign_brief.get("hashtags_mentions") or []

    has_brief_content = any([brand_overview, deliverables, timeline, hashtags])

    if has_brief_content:
        lines = []
        # Intro line
        lines.append(f"Great! We're happy to proceed{final_price_text}.")
        lines.append("")  # blank line before brief

        # Campaign brief heading + overview
        lines.append("Campaign brief:")
        if brand_overview:
            lines.append(brand_overview.strip())

        # Deliverables
        if deliverables:
            lines.append("")
            lines.append("Key deliverables:")
            for item in deliverables:
                lines.append(f"- {item}")

        # Timeline
        if timeline:
            lines.append("")
            lines.append("Timeline:")
            for item in timeline:
                lines.append(f"- {item}")

        # Hashtags / mentions
        if hashtags:
            lines.append("")
            lines.append("Hashtags and mentions:")
            for tag in hashtags:
                lines.append(f"- {tag}")

        lines.append("")
        lines.append(
            "We'll share any remaining operational details and next steps shortly."
        )

        state["final_reply"] = "\n".join(lines)
    else:
        state["final_reply"] = (
            f"Great! We're happy to proceed{final_price_text}. "
            "We'll share the full campaign details and next steps shortly."
        )

    state["next_action"] = NextAction.CLOSE_CONVERSATION

    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        await collection.update_one(
            {"_id": ObjectId(state["_id"])},
            {
                "$set": {
                    "negotiation_status": state["negotiation_status"],
                    "negotiation_completed": True,
                    "final_reply": state["final_reply"],
                    "last_offered_price": state.get("last_offered_price"),
                    "next_action": state["next_action"],
                    "conversation_mode": state.get("conversation_mode"),
                    "human_takeover": state.get("human_takeover"),
                    "agent_paused": state.get("agent_paused"),
                }
            },
        )
    except Exception as e:
        print(f"[accept_negotiation_node] Mongo persistence failed: {e}")

    print(f"{Colors.CYAN}Negotiation accepted. Reply: {state['final_reply']}")
    print(f"{Colors.YELLOW}Exiting from accept_negotiation_node")
    print("--------------------------------")
    return state

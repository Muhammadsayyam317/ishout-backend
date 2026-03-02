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

    final_price = state.get("last_offered_price")
    if final_price is None:
        final_price_text = ""
    else:
        final_price_text = f" at ${final_price:.2f}"

    # If we have a campaign brief, append a short summary to the acceptance message.
    campaign_brief = state.get("campaign_brief") or {}
    brand_overview = campaign_brief.get("brand_name_influencer_campaign_brief")
    deliverables = campaign_brief.get("deliverables_per_influencer") or []
    timeline = campaign_brief.get("timeline") or []
    hashtags = campaign_brief.get("hashtags_mentions") or []

    brief_parts = []
    if brand_overview:
        brief_parts.append(brand_overview)
    if deliverables:
        deliverables_text = "; ".join(deliverables)
        brief_parts.append(f"Key deliverables: {deliverables_text}.")
    if timeline:
        timeline_text = "; ".join(timeline)
        brief_parts.append(f"High-level timeline: {timeline_text}.")
    if hashtags:
        hashtags_text = ", ".join(hashtags)
        brief_parts.append(f"Hashtags and mentions: {hashtags_text}.")

    brief_summary = " ".join(brief_parts)

    if brief_summary:
        state["final_reply"] = (
            f"Great! We're happy to proceed{final_price_text}. "
            f"{brief_summary} "
            "We'll share any remaining operational details shortly."
        )
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
                }
            },
        )
    except Exception as e:
        print(f"[accept_negotiation_node] Mongo persistence failed: {e}")

    print(f"{Colors.CYAN}Negotiation accepted. Reply: {state['final_reply']}")
    print(f"{Colors.YELLOW}Exiting from accept_negotiation_node")
    print("--------------------------------")
    return state

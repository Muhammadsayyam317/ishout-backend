from app.Schemas.instagram.negotiation_schema import NextAction
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.message_context import build_campaign_brief_pdf_bytes, upload_media_to_meta
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

    short_intro = f"Great! We're happy to proceed{final_price_text}."
    state["final_reply"] = short_intro

    # Try to build and upload a campaign brief PDF if we have a brief on state.
    campaign_brief = state.get("campaign_brief") or {}
    media_id = None
    pdf_filename = None

    if campaign_brief:
        try:
            pdf_bytes = build_campaign_brief_pdf_bytes(campaign_brief)
            if pdf_bytes:
                title = (campaign_brief.get("title") or "campaign_brief").strip()
                safe_title = "".join(
                    c for c in title if c.isalnum() or c in (" ", "_", "-")
                ).strip() or "campaign_brief"
                pdf_filename = f"{safe_title}.pdf"
                media_id = await upload_media_to_meta(
                    pdf_bytes, "application/pdf", pdf_filename
                )
            else:
                print(
                    f"{Colors.YELLOW}[accept_negotiation_node] Skipping PDF upload: brief did not produce content"
                )
        except Exception as e:
            print(f"{Colors.RED}[accept_negotiation_node] PDF build/upload failed: {e}")

    if media_id:
        state["final_reply"] = (
            f"{short_intro} Please find the campaign brief attached."
        )
        state["brief_media_id"] = media_id
        state["brief_media_filename"] = pdf_filename or "campaign_brief.pdf"

    state["next_action"] = NextAction.CLOSE_CONVERSATION

    # Append the final reply to in-memory history so negotiation dashboards
    # see the last AI message in the conversation thread.
    state.setdefault("history", []).append(
        {"sender_type": "AI", "message": state["final_reply"]}
    )

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

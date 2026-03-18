from datetime import datetime, timezone
from app.Schemas.instagram.negotiation_schema import NextAction
from app.Schemas.whatsapp.negotiation_schema import WhatsappNegotiationState
from app.utils.campaign_helpers import upload_file_to_s3_with_prefix
from app.utils.message_context import build_campaign_brief_pdf_bytes, upload_media_to_meta
from app.utils.printcolors import Colors
from app.db.connection import get_db
from bson import ObjectId
from app.config.credentials_config import config


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
    s3_url = None

    if campaign_brief:
        try:
            pdf_bytes = build_campaign_brief_pdf_bytes(campaign_brief)
            if pdf_bytes:
                title = (campaign_brief.get("title") or "campaign_brief").strip()
                safe_title = "".join(
                    c for c in title if c.isalnum() or c in (" ", "_", "-")
                ).strip() or "campaign_brief"
                pdf_filename = f"{safe_title}.pdf"

                # Upload to Meta (for WhatsApp delivery)
                media_id = await upload_media_to_meta(
                    pdf_bytes, "application/pdf", pdf_filename
                )

                # Also upload to S3 so dashboards can show the exact PDF via URL.
                try:
                    s3_url = await upload_file_to_s3_with_prefix(
                        prefix_folder="campaign_briefs",
                        object_id=str(state.get("influencer_id") or ""),
                        filename=pdf_filename,
                        content_type="application/pdf",
                        file_bytes=pdf_bytes,
                    )
                except Exception as e:
                    print(
                        f"{Colors.RED}[accept_negotiation_node] S3 upload failed: {e}"
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
        {
            "sender_type": "AI",
            "message": state["final_reply"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    # If we have an S3 URL for the PDF, store it as a separate AI message so
    # frontends can detect it and render a direct PDF download/preview.
    if s3_url:
        state["history"].append(
            {
                "sender_type": "AI",
                "message": s3_url,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        state["brief_s3_url"] = s3_url

    influencer_id = state.get("influencer_id")
    if not influencer_id:
        print(f"{Colors.RED}[accept_negotiation_node] Missing influencer_id; skip campaign_influencers update")
    else:
        try:
            db = get_db()
            collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_CAMPAIGN_INFLUENCERS)
            await collection.update_one(
                {"_id": ObjectId(influencer_id)},
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

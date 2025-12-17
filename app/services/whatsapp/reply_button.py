from bson import ObjectId
from datetime import datetime, timezone
from app.db.connection import get_db


async def handle_button_reply(message: dict):
    interactive = message.get("interactive", {})
    button = interactive.get("button_reply", {})
    button_id = button.get("id")

    if not button_id:
        return

    print("🔘 Button clicked:", button_id)
    db = get_db()
    influencers = db.get_collection("campaign_influencers")

    if button_id.startswith("approve_"):
        influencer_id = button_id.replace("approve_", "")
        status = "approved"
        company_approved = True

    elif button_id.startswith("reject_"):
        influencer_id = button_id.replace("reject_", "")
        status = "rejected"
        company_approved = False

    else:
        return

    result = await influencers.update_one(
        {"_id": ObjectId(influencer_id)},
        {
            "$set": {
                "status": status,
                "company_approved": company_approved,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    print(
        f"✅ Influencer {influencer_id} updated → {status} | matched={result.matched_count}"
    )

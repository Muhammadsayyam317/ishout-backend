from bson import ObjectId
from app.db.connection import get_db
from app.agents.nodes.message_to_whatsapp import send_whatsapp_message


async def send_whatsapp_approved_influencers(campaign_id: str):
    print("\n--- STARTING APPROVED INFLUENCERS WHATSAPP CAROUSEL TASK ---")

    db = get_db()

    campaigns = db["campaigns"]
    influencers_collection = db["campaign_influencers"]

    campaign = await campaigns.find_one({"_id": ObjectId(campaign_id)})
    if not campaign:
        print("Campaign not found")
        return

    user_phone = campaign.get("user_id")
    influencers = await influencers_collection.find(
        {"campaign_id": ObjectId(campaign_id), "status": "approved"}
    ).to_list(100)

    if not influencers:
        print("No approved influencers")
        return

    cards = []
    for idx, inf in enumerate(influencers, start=1):

        cards.append(
            {
                "title": f"@{inf.get('username')}",
                "description": (
                    f"Followers: {inf.get('followers')}\n"
                    f"Country: {inf.get('country')}\n"
                    f"Pricing: {inf.get('pricing')}"
                ),
                "media": {
                    "type": "image",
                    "link": inf.get("pic"),
                },
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": f"approve_{inf.get('influencer_id')}",
                            "title": "Approve",
                        },
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": f"reject_{inf.get('influencer_id')}",
                            "title": "Reject",
                        },
                    },
                ],
            }
        )

    payload = {
        "messaging_product": "whatsapp",
        "to": user_phone,
        "type": "interactive",
        "interactive": {
            "type": "carousel",
            "body": {"text": "🎉 Your approved influencers are ready!"},
            "carousel": {"cards": cards},
        },
    }

    success = await send_whatsapp_message(payload)

    if success:
        print("Carousel sent successfully!")
    else:
        print("Failed to send carousel message")

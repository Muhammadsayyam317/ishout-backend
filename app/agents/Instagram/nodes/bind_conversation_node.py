import datetime
from app.config.credentials_config import config
from app.db.connection import get_db


async def bind_conversation_to_influencer(
    *,
    thread_id: str,
    influencer: dict,
):
    print("Enter into bind conversation to influencer")
    db = get_db()
    conv = db.get_collection(config.INSTAGRAM_MESSAGE_COLLECTION)

    await conv.update_one(
        {"thread_id": thread_id},
        {
            "$setOnInsert": {
                "thread_id": thread_id,
                "platform": "instagram",
                "influencer_id": influencer["influencer_id"],
                "campaign_id": influencer["campaign_id"],
                "company_user_id": influencer["company_user_id"],
                "min_price": influencer["min_price"],
                "max_price": influencer["max_price"],
                "currency": "USD",
                "negotiation_stage": "INITIAL",
                "ai_enabled": True,
                "created_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )
    print("Exiting from bind conversation to influencer")

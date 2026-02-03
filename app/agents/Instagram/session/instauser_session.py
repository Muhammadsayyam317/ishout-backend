from app.Schemas.instagram.negotiation_schema import InfluencerDetails
from app.db.connection import get_db
from app.core.exception import InternalServerErrorException
from datetime import datetime, timezone


async def instauser_session(thread_id: str, influencer_details: InfluencerDetails):
    """
    Store or update Instagram session info for dashboard.
    """
    try:
        db = get_db()
        collection = db.get_collection("instagram_sessions")
        influencer_details["last_updated"] = datetime.now(timezone.utc)

        await collection.update_one(
            {"thread_id": thread_id}, {"$set": influencer_details}, upsert=True
        )

        print(f"Instagram session updated for thread_id: {thread_id}")
        return True
    except Exception as e:
        raise InternalServerErrorException(f"Error in instauser_session: {e}") from e

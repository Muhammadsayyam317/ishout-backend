from app.Schemas.instagram.negotiation_schema import InfluencerDetails
from app.core.exception import InternalServerErrorException
from app.db.connection import get_db


async def instauser_session(thread_id: str, influencer_details: InfluencerDetails):
    try:
        db = get_db()
        collection = db.get_collection("instagram_sessions")
        await collection.update_one(
            {"thread_id": thread_id}, {"$set": influencer_details}, upsert=True
        )
        print(f"Instagram user session updated for thread_id: {thread_id}")
        return True
    except Exception as e:
        raise InternalServerErrorException(f"Error in instauser_session: {e}") from e

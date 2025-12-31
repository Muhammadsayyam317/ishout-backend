from fastapi import HTTPException
from app.config import config
from app.core.exception import (
    BadRequestException,
    InternalServerErrorException,
    NotFoundException,
)
from app.db.connection import get_db
from app.Schemas.influencers import DeleteInfluencerRequest


PLATFORM_COLLECTIONS = {
    "instagram": config.MONGODB_ATLAS_COLLECTION_INSTAGRAM,
    "tiktok": config.MONGODB_ATLAS_COLLECTION_TIKTOK,
    "youtube": config.MONGODB_ATLAS_COLLECTION_YOUTUBE,
}


async def deleteInfluencerEmbedding(request: DeleteInfluencerRequest):
    try:
        if not request.platform or not request.influencer_id:
            raise BadRequestException(
                status_code=400, detail="platform and influencer_id are required"
            )

        collection_name = PLATFORM_COLLECTIONS.get(request.platform.lower())
        if not collection_name:
            raise BadRequestException(
                message=f"Invalid platform '{request.platform}'. Use instagram, tiktok, or youtube.",
            )

        db = get_db()
        platform_collection = db.get_collection(collection_name)
        delete_result = await platform_collection.delete_one(
            {"id": request.influencer_id}
        )
        if delete_result.deleted_count == 0:
            raise NotFoundException(
                status_code=404, detail="Influencer not found in the specified platform"
            )
        metadata_collection = db.get_collection("campaign_influencers")
        metadata_deleted_count = (
            await metadata_collection.delete_many(
                {"influencer_id": request.influencer_id}
            )
        ).deleted_count

        return {
            "message": "Influencer deleted successfully",
            "platform_deleted_count": delete_result.deleted_count,
            "metadata_deleted_count": metadata_deleted_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in delete influencer embedding: {str(e)}"
        )

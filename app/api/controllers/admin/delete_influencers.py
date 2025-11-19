from bson import ObjectId
from fastapi import HTTPException
from app.db.connection import get_db
from app.models.influencers_model import DeleteInfluencerRequest
from app.services.embedding_service import delete_from_vector_store


async def deleteInfluencerEmbedding(request: DeleteInfluencerRequest):
    try:
        result = await delete_from_vector_store(
            platform=request.platform,
            influencer_id=request.influencer_id,
        )
        if result.get("deleted_count", 0) == 0:
            raise HTTPException(
                status_code=400,
                detail="No matching document found to delete influencer",
            )
        metadata_result = await _delete_influencer_metadata(request.influencer_id)

        return {
            "embedding": result,
            "metadata_deleted_count": metadata_result.get("deleted_count", 0),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in delete influencer embedding: {str(e)}"
        ) from e


async def _delete_influencer_metadata(influencer_id: str):
    """Remove influencer metadata stored in campaign_influencers collection."""
    try:
        influencer_object_id = ObjectId(influencer_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid influencer_id format for metadata deletion",
        )

    db = get_db()
    collection = db.get_collection("campaign_influencers")
    result = await collection.delete_many({"influencer_id": influencer_object_id})
    return {"deleted_count": result.deleted_count}

from fastapi import APIRouter, HTTPException
from app.models.influencers_model import DeleteInfluencerRequest
from app.services.embedding_service import delete_from_vector_store

router = APIRouter()


@router.delete("/delete-influencer", tags=["Admin"])
async def delete_influencer_route(request: DeleteInfluencerRequest):
    """Delete influencer data and embeddings from the platform collection.

    Accepts one of: document_id (preferred), username, or url.
    """
    try:
        result = await delete_from_vector_store(
            platform=request.platform,
            influencer_id=request.influencer_id,
        )
        if result.get("deleted_count", 0) == 0:
            raise HTTPException(
                status_code=400, detail="No matching document found to delete"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

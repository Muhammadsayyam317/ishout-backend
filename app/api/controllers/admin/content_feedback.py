from datetime import datetime, timezone
from typing import Any, Dict

from bson import ObjectId

from app.Schemas.content_feedback import (
    ContentFeedbackDocument,
    ContentFeedbackUpsertRequest,
    ReviewBlock,
)
from app.config.credentials_config import config
from app.core.exception import BadRequestException, InternalServerErrorException
from app.db.connection import get_db
from app.utils.helpers import convert_objectid


def _review_field(review_side: str) -> str:
    if review_side == "admin_review":
        return "admin_Rewiew"
    if review_side == "brand_review":
        return "brand_review"
    raise BadRequestException(
        message="review_side must be admin_review or brand_review"
    )


async def upsert_content_feedback(
    payload: ContentFeedbackUpsertRequest,
) -> Dict[str, Any]:
    """
    Upsert one feedback thread for a specific negotiation + content URL.
    - If exists, append new msg into requested side's message array.
    - If not exists, create a new document with both review blocks.
    """
    try:
        db = get_db()
        collection = db.get_collection(config.MONGODB_CONTENT_FEEDBACK)

        negotiation_id = payload.negotiation_id.strip()
        campaign_id = payload.campaign_id.strip()
        content_url = payload.content_url.strip()
        msg = payload.msg.strip()
        side_field = _review_field(payload.review_side)

        if not (negotiation_id and campaign_id and content_url and msg):
            raise BadRequestException(
                message="negotiation_id, campaign_id, content_url and msg are required"
            )

        now = datetime.now(timezone.utc)
        existing = await collection.find_one(
            {"negotiation_id": negotiation_id, "content_url": content_url}
        )

        if existing:
            await collection.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {"updated_at": now},
                    "$setOnInsert": {"created_at": now},
                    "$push": {f"{side_field}.message": msg},
                },
                upsert=True,
            )
            doc = await collection.find_one({"_id": existing["_id"]})
        else:
            new_doc = ContentFeedbackDocument(
                feedback_id=str(ObjectId()),
                negotiation_id=negotiation_id,
                campaign_id=campaign_id,
                content_url=content_url,
                admin_Rewiew=ReviewBlock(
                    content_url=content_url,
                    message=[msg] if side_field == "admin_Rewiew" else [],
                ),
                brand_review=ReviewBlock(
                    content_url=content_url,
                    message=[msg] if side_field == "brand_review" else [],
                ),
                created_at=now,
                updated_at=now,
            ).model_dump()
            await collection.insert_one(new_doc)
            doc = await collection.find_one(
                {"negotiation_id": negotiation_id, "content_url": content_url}
            )

        return {
            "success": True,
            "message": "Content feedback saved successfully",
            "feedback": convert_objectid(doc) if doc else None,
        }
    except BadRequestException:
        raise
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in upsert_content_feedback: {str(e)}"
        ) from e


async def get_content_feedback_admin(feedback_id: str) -> Dict[str, Any]:
    """Admin side: return both admin and brand review blocks by feedback_id."""
    try:
        db = get_db()
        collection = db.get_collection(config.MONGODB_CONTENT_FEEDBACK)
        fb_id = (feedback_id or "").strip()
        if not fb_id:
            raise BadRequestException(message="feedback_id is required")

        doc = await collection.find_one({"feedback_id": fb_id})
        if not doc:
            raise BadRequestException(message="feedback not found for feedback_id")
        doc = convert_objectid(doc)

        return {
            "success": True,
            "feedback": doc,
        }
    except BadRequestException:
        raise
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in get_content_feedback_admin: {str(e)}"
        ) from e


async def get_content_feedback_brand(feedback_id: str) -> Dict[str, Any]:
    """Brand side: return only brand review messages by feedback_id."""
    try:
        db = get_db()
        collection = db.get_collection(config.MONGODB_CONTENT_FEEDBACK)
        fb_id = (feedback_id or "").strip()
        if not fb_id:
            raise BadRequestException(message="feedback_id is required")

        d = await collection.find_one({"feedback_id": fb_id})
        if not d:
            raise BadRequestException(message="feedback not found for feedback_id")
        item = convert_objectid(d)

        return {
            "success": True,
            "feedback": {
                "feedback_id": item.get("feedback_id"),
                "negotiation_id": item.get("negotiation_id"),
                "campaign_id": item.get("campaign_id"),
                "content_url": item.get("content_url"),
                "brand_review": item.get("brand_review", {}),
                "updated_at": item.get("updated_at"),
            },
        }
    except BadRequestException:
        raise
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in get_content_feedback_brand: {str(e)}"
        ) from e

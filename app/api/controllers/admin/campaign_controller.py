from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException, BackgroundTasks
from app.api.controllers.admin.influencers_controller import (
    find_influencers_by_campaign,
)
from app.Schemas.campaign_influencers import (
    CampaignInfluencerStatus,
    CampaignInfluencersRequest,
)
from app.Schemas.campaign import (
    CreateCampaignRequest,
    AdminGenerateInfluencersRequest,
    CampaignStatusUpdateRequest,
    CampaignStatus,
)
from app.Schemas.influencers import AddInfluencerNumberRequest, FindInfluencerRequest
from app.core.exception import (
    BadRequestException,
    InternalServerErrorException,
    NotFoundException,
    UnauthorizedException,
)
from app.db.connection import get_db
from app.config import config
from app.services.whatsapp.interactive_message import (
    send_whatsapp_interactive_message,
)
from app.utils.helpers import convert_objectid


async def _populate_user_details(user_id: str) -> Dict[str, Any]:
    try:
        if not user_id:
            return None
        db = get_db()
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise NotFoundException(message="User not found")

        return {
            "user_id": str(user["_id"]),
            "company_name": user.get("company_name"),
            "email": user.get("email"),
            "contact_person": user.get("contact_person"),
            "phone": user.get("phone"),
            "industry": user.get("industry"),
            "company_size": user.get("company_size"),
        }
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error populating user details: {str(e)}"
        ) from e


async def _populate_influencer_details(
    influencer_ids: List[str], platform: Optional[str] = None
) -> List[Dict[str, Any]]:
    try:
        if not influencer_ids:
            raise BadRequestException(message="No influencer IDs provided")
        platforms_to_check = (
            [platform] if platform else ["instagram", "tiktok", "youtube"]
        )
        collections_to_check = []

        for plat in platforms_to_check:
            if plat == "instagram":
                collection_name = config.MONGODB_ATLAS_COLLECTION_INSTAGRAM
            elif plat == "tiktok":
                collection_name = config.MONGODB_ATLAS_COLLECTION_TIKTOK
            elif plat == "youtube":
                collection_name = config.MONGODB_ATLAS_COLLECTION_YOUTUBE
            else:
                continue

            if collection_name:
                collections_to_check.append((collection_name, plat))

        for inf_id in influencer_ids:
            for collection_name, plat in collections_to_check:
                try:
                    db = get_db()
                    collection = db.get_collection(collection_name)
                    influencer = await collection.find_one({"_id": ObjectId(inf_id)})
                    if influencer:
                        influencer["_id"] = str(influencer["_id"])
                        influencer["platform"] = platform
                        return influencer
                except Exception as e:
                    raise InternalServerErrorException(
                        message=f"Error populating influencer details: {str(e)}",
                    ) from e
        raise NotFoundException(
            message=f"Influencer {inf_id} not found in any platform"
        )
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error populating influencer details: {str(e)}"
        ) from e


async def create_campaign(request_data: CreateCampaignRequest) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign_name = request_data.name
        if not campaign_name:
            campaign_name = f"Campaign - {', '.join(request_data.category)} - {', '.join(request_data.platform)}"

        campaign_doc = {
            "name": campaign_name,
            "platform": request_data.platform,
            "category": request_data.category,
            "followers": request_data.followers,
            "country": request_data.country,
            "user_id": request_data.user_id,
            "company_name": request_data.company_name,
            "user_type": "Website",
            "status": CampaignStatus.PENDING,
            "limit": request_data.limit,
            "generated": False,
            "brief_id": request_data.brief_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        await campaigns_collection.insert_one(campaign_doc)
        return {
            "message": "Campaign created successfully",
        }

    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in creating campaign: {str(e)}"
        ) from e


async def get_all_campaigns(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        users_collection = db.get_collection("users")

        query = {}

        if status:
            try:
                valid_status = {
                    CampaignStatus.PENDING,
                    CampaignStatus.PROCESSING,
                    CampaignStatus.APPROVED,
                    CampaignStatus.COMPLETED,
                    CampaignStatus.REJECTED,
                }

                if status not in valid_status and status not in {
                    s.value for s in valid_status
                }:
                    raise BadRequestException(
                        message="Invalid status. Use pending, processing, approved, completed, or rejected.",
                    )

                normalized = (
                    status.value if isinstance(status, CampaignStatus) else str(status)
                )
                query["status"] = normalized

            except Exception as e:
                raise BadRequestException(
                    message=f"Invalid status: {str(e)}",
                ) from e

        skip = (page - 1) * page_size
        total_count = await campaigns_collection.count_documents(query)

        campaigns = (
            await campaigns_collection.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(page_size)
            .to_list(length=None)
        )

        # Collect unique user_ids
        user_ids = list(
            {
                campaign.get("user_id")
                for campaign in campaigns
                if campaign.get("user_id")
            }
        )
        object_user_ids = []
        for uid in user_ids:
            try:
                object_user_ids.append(ObjectId(uid))
            except Exception:
                continue

        users = await users_collection.find(
            {"_id": {"$in": object_user_ids}}, {"logo_url": 1}
        ).to_list(length=None)

        user_logo_map = {str(user["_id"]): user.get("logo_url") for user in users}
        for campaign in campaigns:
            campaign["logo_url"] = user_logo_map.get(campaign.get("user_id"))
        campaigns = [convert_objectid(doc) for doc in campaigns]

        total_pages = (total_count + page_size - 1) // page_size

        return {
            "campaigns": campaigns,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    except Exception as e:
        return HTTPException(
            status_code=500, detail=f"Error in get_all_campaigns: {str(e)}"
        )


async def AdminApprovedSingleInfluencer(
    request_data: CampaignInfluencersRequest,
):
    try:
        db = get_db()
        campaign_collection = db.get_collection("campaign_influencers")
        generated_collection = db.get_collection("generated_influencers")

        campaign_id = ObjectId(request_data.campaign_id)
        influencer_id_str = request_data.influencer_id
        influencer_id_obj = ObjectId(request_data.influencer_id)
        is_admin_approved = request_data.status == CampaignInfluencerStatus.APPROVED

        update_fields = {
            "username": request_data.username,
            "picture": request_data.picture,
            "engagementRate": request_data.engagementRate,
            "bio": request_data.bio,
            "followers": request_data.followers,
            "country": request_data.country,
            "status": request_data.status.value,
            "company_user_id": request_data.company_user_id,
            "pricing": request_data.pricing,
            "admin_approved": is_admin_approved,
            "updated_at": datetime.now(timezone.utc),
        }

        existing = await campaign_collection.find_one(
            {
                "campaign_id": campaign_id,
                "influencer_id": influencer_id_obj,
                "platform": request_data.platform,
            }
        )

        if existing:
            await campaign_collection.update_one(
                {
                    "campaign_id": campaign_id,
                    "influencer_id": influencer_id_obj,
                    "platform": request_data.platform,
                },
                {"$set": update_fields},
            )
        else:
            await campaign_collection.insert_one(
                {
                    **update_fields,
                    "campaign_id": campaign_id,
                    "influencer_id": influencer_id_obj,
                    "platform": request_data.platform,
                    "company_approved": False,
                }
            )

        result = await generated_collection.update_one(
            {
                "campaign_id": campaign_id,
                "influencer_id": influencer_id_str,
            },
            {
                "$set": {
                    "admin_approved": is_admin_approved,
                    "status": request_data.status.value,
                    "pricing": request_data.pricing,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        if result.matched_count == 0:
            raise NotFoundException(
                message="Generated influencer not found",
            )

        return {
            "message": "Influencer approved and synced successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error approving influencer: {str(e)}",
        )


async def storeInfluencerNumber(
    request_data: AddInfluencerNumberRequest,
):
    try:
        db = get_db()
        instagram_collection = db.get_collection(
            config.MONGODB_ATLAS_COLLECTION_INSTAGRAM
        )
        tiktok_collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_TIKTOK)
        youtube_collection = db.get_collection(config.MONGODB_ATLAS_COLLECTION_YOUTUBE)
        if request_data.platform == "instagram":
            result = await instagram_collection.insert_one(
                {
                    "influencer_id": ObjectId(request_data.influencer_id),
                    "phone_number": request_data.phone_number,
                }
            )
        elif request_data.platform == "tiktok":
            result = await tiktok_collection.insert_one(
                {
                    "influencer_id": ObjectId(request_data.influencer_id),
                    "phone_number": request_data.phone_number,
                }
            )
        elif request_data.platform == "youtube":
            result = await youtube_collection.insert_one(
                {
                    "influencer_id": ObjectId(request_data.influencer_id),
                    "phone_number": request_data.phone_number,
                }
            )
        if result.inserted_id:
            return {"message": "Influencer number stored successfully"}
        else:
            raise NotFoundException(message="Failed to store influencer number")
    except HTTPException:
        raise
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in store influencer number: {str(e)}"
        ) from e


async def add_influencer_Number(
    request_data: AddInfluencerNumberRequest,
):
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaign_influencers")
        campaign = await campaigns_collection.find_one(
            {"influencer_id": ObjectId(request_data.influencer_id)}
        )
        if not campaign:
            raise NotFoundException(message="Influencer not found")
        campaign["phone_number"] = request_data.phone_number
        result = await campaigns_collection.update_one(
            {"influencer_id": ObjectId(request_data.influencer_id)},
            {
                "$set": {
                    "phone_number": request_data.phone_number,
                    "max_price": request_data.max_price,
                    "min_price": request_data.min_price,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Failed to update influencer")
        if request_data.phone_number and request_data.platform:
            await storeInfluencerNumber(request_data)
        return {
            "message": "Influencer details updated successfully",
            "influencer_id": request_data.influencer_id,
            "phone_number": request_data.phone_number,
            "platform": request_data.platform,
            "max_price": request_data.max_price,
            "min_price": request_data.min_price,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in add influencer number: {str(e)}"
        ) from e


async def user_reject_influencers(
    campaign_id: str, influencer_ids: List[str], user_id: str
) -> Dict[str, Any]:
    try:
        if not influencer_ids:
            raise BadRequestException(message="No influencer IDs provided")
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise NotFoundException(message="Campaign not found")

        if campaign.get("user_id") != user_id:
            raise UnauthorizedException(
                message="You don't have permission to modify this campaign",
            )

        current_influencer_ids = campaign.get("influencer_ids", [])
        current_references = campaign.get("influencer_references", [])
        current_rejected_by_user = campaign.get("rejectedByUser", [])

        rejected_influencers = []
        remaining_approved_ids = []
        remaining_references = []

        for inf_id in influencer_ids:
            if inf_id in current_influencer_ids:
                rejected_influencers.append(inf_id)
                current_rejected_by_user.append(inf_id)
            else:
                return {
                    "error": f"Influencer {inf_id} is not approved for this campaign"
                }

        for inf_id in current_influencer_ids:
            if inf_id not in influencer_ids:
                remaining_approved_ids.append(inf_id)

        for ref in current_references:
            if ref.get("influencer_id") not in influencer_ids:
                remaining_references.append(ref)

        result = await campaigns_collection.update_one(
            {"_id": ObjectId(campaign_id)},
            {
                "$set": {
                    "influencer_ids": remaining_approved_ids,
                    "influencer_references": remaining_references,
                    "rejectedByUser": current_rejected_by_user,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        if result.modified_count == 0:
            return {"error": "Failed to update campaign"}

        return {
            "message": f"Successfully rejected {len(rejected_influencers)} influencer(s)",
            "campaign_id": campaign_id,
            "rejected_influencer_ids": rejected_influencers,
            "remaining_approved_count": len(remaining_approved_ids),
            "total_rejected_by_user": len(current_rejected_by_user),
        }
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in user reject influencers: {str(e)}"
        ) from e


async def add_rejected_influencers(
    campaign_id: str, rejected_ids: List[str]
) -> Dict[str, Any]:
    try:
        if not rejected_ids:
            raise BadRequestException(message="No rejected ids provided")
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        existing_rejected: List[str] = campaign.get("rejected_ids", []) or []
        combined = list(dict.fromkeys(existing_rejected + rejected_ids))

        result = await campaigns_collection.update_one(
            {"_id": ObjectId(campaign_id)},
            {"$set": {"rejected_ids": combined, "updated_at": datetime.utcnow()}},
        )

        if result.modified_count == 0:
            raise InternalServerErrorException(
                message="Failed to update campaign with rejected ids"
            )

        return {
            "message": "Rejected influencers recorded",
            "total_rejected": len(combined),
        }
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in add rejected influencers: {str(e)}"
        ) from e


async def admin_generate_influencers(
    campaign_id: str,
    request_data: AdminGenerateInfluencersRequest,
    background_tasks: BackgroundTasks,
):
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise NotFoundException(message="Campaign not found")
        campaign_limit = campaign.get("limit") or request_data.limit
        influencer_request = FindInfluencerRequest(
            campaign_id=campaign_id,
            user_id=campaign.get("user_id", ""),
            limit=campaign_limit,
        )
        influencers = await find_influencers_by_campaign(influencer_request)
        background_tasks.add_task(
            store_generated_influencers,
            campaign_id,
            influencers,
        )
        return influencers
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in admin generate influencers: {str(e)}"
        ) from e


async def store_generated_influencers(
    campaign_id: str,
    influencers: List[Dict[str, Any]],
):
    try:
        db = get_db()
        collection = db.get_collection("generated_influencers")
        campaign_collection = db.get_collection("campaigns")
        documents = []

        for inf in influencers:
            if not isinstance(inf, dict):
                continue

            documents.append(
                {
                    "campaign_id": ObjectId(campaign_id),
                    "influencer_id": inf.get("id"),
                    "username": inf.get("username"),
                    "platform": inf.get("platform"),
                    "followers": inf.get("followers"),
                    "engagementRate": inf.get("engagementRate"),
                    "country": inf.get("country"),
                    "bio": inf.get("bio"),
                    "picture": inf.get("picture"),
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
            )
            await campaign_collection.update_one(
                {"_id": ObjectId(campaign_id)},
                {"$set": {"generated": True}},
            )

        if documents:
            await collection.insert_many(documents)
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in store generated influencers: {str(e)}"
        ) from e


async def update_campaignstatus_with_background_task(
    request_data: CampaignStatusUpdateRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        influencers_collection = db.get_collection("campaign_influencers")
        result = await campaigns_collection.update_one(
            {"_id": ObjectId(request_data.campaign_id)},
            {
                "$set": {
                    "status": request_data.status,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        if result.modified_count == 0:
            raise NotFoundException(message="No changes")
        campaign = await campaigns_collection.find_one(
            {"_id": ObjectId(request_data.campaign_id)}
        )

        if not campaign:
            raise NotFoundException(message="Campaign not found")

        user_type = campaign.get("user_type", None)
        if request_data.status == CampaignStatus.APPROVED and user_type == "whatsapp":
            whatsapp_phone = campaign.get("whatsapp_phone")
            if not whatsapp_phone:
                raise NotFoundException(
                    message="WhatsApp phone number not found in campaign",
                )

            approved_influencers = influencers_collection.find(
                {
                    "campaign_id": ObjectId(campaign["_id"]),
                    "admin_approved": True,
                    "status": CampaignInfluencerStatus.APPROVED.value,
                }
            )
            approved_influencers = await approved_influencers.to_list(length=None)
            for influencer in approved_influencers:
                username = influencer.get("username")
                if not username:
                    continue
                background_tasks.add_task(
                    send_whatsapp_interactive_message,
                    whatsapp_phone,
                    "Approve or Reject this influencer?",
                    influencer,
                )

        return {
            "message": f"Campaign status updated to {request_data.status}",
            "campaign_id": request_data.campaign_id,
            "status": request_data.status,
        }

    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in update_campaign_status: {str(e)}",
        ) from e


async def update_status(request_data: CampaignStatusUpdateRequest) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        result = await campaigns_collection.update_one(
            {"_id": ObjectId(request_data.campaign_id)},
            {
                "$set": {
                    "status": request_data.status,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        if result.modified_count == 0:
            raise NotFoundException(message="No changes")

        return {
            "message": f"Campaign status updated to {request_data.status}",
            "campaign_id": request_data.campaign_id,
            "status": request_data.status,
        }
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in update status: {str(e)}",
        ) from e


async def get_campaign_generated_influencers(campaign_id: str) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise NotFoundException(message="Campaign not found")

        generated_influencer_ids = campaign.get("generated_influencers", [])

        generated_influencers_with_details = []
        if generated_influencer_ids and isinstance(generated_influencer_ids[0], str):
            generated_influencers_with_details = await _populate_influencer_details(
                generated_influencer_ids
            )
        else:
            generated_influencers_with_details = generated_influencer_ids

        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign["name"],
            "status": campaign.get("status"),
            "generated_influencers": generated_influencers_with_details,
            "total_generated": len(generated_influencers_with_details),
        }

    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in get campaign generated influencers: {str(e)}",
        ) from e


async def company_approved_campaign_influencers(
    campaign_id: str,
    page: int = 1,
    page_size: int = 10,
):
    if not campaign_id:
        raise BadRequestException(message="campaign_id is required")
    if page < 1 or page_size < 1:
        raise BadRequestException(message="Invalid pagination parameters")

    try:
        campaign_object_id = ObjectId(campaign_id)
    except Exception:
        raise BadRequestException(message="Invalid campaign_id format")

    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        base_query = {
            "campaign_id": campaign_object_id,
            "admin_approved": True,
            "company_approved": True,
            "status": CampaignInfluencerStatus.APPROVED.value,
        }

        cursor = (
            collection.find(base_query)
            .sort("updated_at", -1)
            .skip((page - 1) * page_size)
            .limit(page_size)
        )

        influencers = await cursor.to_list(length=page_size)
        influencers = [convert_objectid(doc) for doc in influencers]

        total = await collection.count_documents(base_query)
        total_pages = (total + page_size - 1) // page_size

        return {
            "campaign_id": campaign_id,
            "influencers": influencers,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error in company approved campaign influencers: {str(e)}",
        ) from e

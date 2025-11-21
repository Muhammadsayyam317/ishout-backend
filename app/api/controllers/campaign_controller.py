from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException
from app.models.campaign_influencers_model import (
    CampaignInfluencerStatus,
    CampaignInfluencersRequest,
)
from app.models.campaign_model import (
    CreateCampaignRequest,
    AdminGenerateInfluencersRequest,
    CampaignStatusUpdateRequest,
    CampaignStatus,
)
from app.models.influencers_model import FindInfluencerRequest
from app.api.controllers.influencers_controller import find_influencers_by_campaign
from app.db.connection import get_db
from app.config import config
from app.utils.helpers import convert_objectid


async def _populate_user_details(user_id: str) -> Dict[str, Any]:
    """Populate user details from user_id"""
    try:
        if not user_id:
            return None
        db = get_db()
        users_collection = db.get_collection("users")
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

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
        print(f"Error populating user details: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error populating user details: {str(e)}"
        ) from e


async def _populate_influencer_details(
    influencer_ids: List[str], platform: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Populate influencer details from influencer IDs"""
    try:
        if not influencer_ids:
            raise HTTPException(status_code=400, detail="No influencer IDs provided")
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
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error populating influencer details: {str(e)}",
                    ) from e
        raise HTTPException(status_code=404, detail=f"Influencer {inf_id} not found")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error populating influencer details: {str(e)}"
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
            "status": CampaignStatus.PENDING,
            "limit": request_data.limit,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        await campaigns_collection.insert_one(campaign_doc)
        return {
            "message": "Campaign created successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in creating campaign: {str(e)}"
        ) from e


async def get_all_campaigns(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
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
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid status. Use pending, processing, approved, completed, or rejected.",
                    )
                normalized = (
                    status.value if isinstance(status, CampaignStatus) else str(status)
                )
                query["status"] = normalized
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status: {str(e)}",
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


async def get_campaign_by_id(campaign_id: str) -> Dict[str, Any]:
    """Get campaign details by ID with populated influencer data"""
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        # Get campaign
        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            return {"error": "Campaign not found"}

        campaign["_id"] = str(campaign["_id"])

        # Get influencer details using optimized queries
        influencer_details = []
        missing_influencers = []

        # Use influencer_references if available (new format), otherwise fall back to legacy
        influencer_references = campaign.get("influencer_references", [])

        if influencer_references:
            # New format: we have platform info
            for ref in influencer_references:
                influencer_id = ref.get("influencer_id")
                platform = ref.get("platform")

                if not influencer_id or not platform:
                    missing_influencers.append(
                        {"id": influencer_id, "reason": "Missing ID or platform"}
                    )
                    continue

                if platform == "instagram":
                    collection_name = config.MONGODB_ATLAS_COLLECTION_INSTAGRAM
                elif platform == "tiktok":
                    collection_name = config.MONGODB_ATLAS_COLLECTION_YOUTUBE
                elif platform == "youtube":
                    collection_name = config.MONGODB_ATLAS_COLLECTION_TIKTOK
                else:
                    missing_influencers.append(
                        {
                            "id": influencer_id,
                            "platform": platform,
                            "reason": "Invalid platform",
                        }
                    )
                    continue

                if not collection_name:
                    missing_influencers.append(
                        {
                            "id": influencer_id,
                            "platform": platform,
                            "reason": f"Collection name not configured for platform {platform}",
                        }
                    )
                    continue

                platform_collection = db.get_collection(collection_name)
                print(
                    "Looking for influencer {} in collection {}".format(
                        influencer_id, collection_name
                    )
                )

                try:
                    influencer = await platform_collection.find_one(
                        {"_id": ObjectId(influencer_id)}
                    )
                    if influencer:
                        influencer["_id"] = str(influencer["_id"])
                        influencer["platform"] = platform
                        # Remove embedding field to reduce payload size
                        if "embedding" in influencer:
                            del influencer["embedding"]
                        influencer_details.append(influencer)
                    else:
                        missing_influencers.append(
                            {
                                "id": influencer_id,
                                "platform": platform,
                                "reason": "Influencer not found",
                            }
                        )
                except Exception:
                    missing_influencers.append(
                        {
                            "id": influencer_id,
                            "platform": platform,
                            "reason": "Invalid ID format",
                        }
                    )
        else:
            # Legacy format: search all platforms (less efficient)
            for influencer_id in campaign.get("influencer_ids", []):
                found = False
                for platform in ["instagram", "tiktok", "youtube"]:
                    # Get collection name from centralized config
                    if platform == "instagram":
                        collection_name = config.MONGODB_ATLAS_COLLECTION_INSTAGRAM
                    elif platform == "tiktok":
                        collection_name = config.MONGODB_ATLAS_COLLECTION_TIKTOK
                    elif platform == "youtube":
                        collection_name = config.MONGODB_ATLAS_COLLECTION_YOUTUBE
                    else:
                        continue

                    if not collection_name:
                        continue

                    platform_collection = db.get_collection(collection_name)

                    try:
                        influencer = await platform_collection.find_one(
                            {"_id": ObjectId(influencer_id)}
                        )
                        if influencer:
                            influencer["_id"] = str(influencer["_id"])
                            influencer["platform"] = platform
                            # Remove embedding field to reduce payload size
                            if "embedding" in influencer:
                                del influencer["embedding"]
                            influencer_details.append(influencer)
                            found = True
                            break
                    except Exception:
                        continue

                if not found:
                    missing_influencers.append(
                        {
                            "id": influencer_id,
                            "reason": "Influencer not found in any platform",
                        }
                    )

        # Get rejected influencer details (rejected by admin)
        rejected_influencer_details = []
        missing_rejected_influencers = []
        rejected_ids = campaign.get("rejected_ids", [])

        for rejected_id in rejected_ids:
            found = False
            for platform in ["instagram", "tiktok", "youtube"]:
                db = get_db()

                if platform == "instagram":
                    collection_name = config.MONGODB_ATLAS_COLLECTION_INSTAGRAM
                elif platform == "tiktok":
                    collection_name = config.MONGODB_ATLAS_COLLECTION_TIKTOK
                elif platform == "youtube":
                    collection_name = config.MONGODB_ATLAS_COLLECTION_YOUTUBE
                else:
                    continue

                if not collection_name:
                    continue

                platform_collection = db.get_collection(collection_name)

                try:
                    influencer = await platform_collection.find_one(
                        {"_id": ObjectId(rejected_id)}
                    )
                    if influencer:
                        influencer["_id"] = str(influencer["_id"])
                        influencer["platform"] = platform
                        # Remove embedding field to reduce payload size
                        if "embedding" in influencer:
                            del influencer["embedding"]
                        rejected_influencer_details.append(influencer)
                        found = True
                        break
                except Exception:
                    continue

            if not found:
                missing_rejected_influencers.append(
                    {
                        "id": rejected_id,
                        "reason": "Rejected influencer not found in any platform",
                    }
                )

        # Get rejected by user influencer details
        rejected_by_user_details = []
        missing_rejected_by_user_influencers = []
        rejected_by_user_ids = campaign.get("rejectedByUser", [])

        for rejected_id in rejected_by_user_ids:
            found = False
            for platform in ["instagram", "tiktok", "youtube"]:
                # Get collection name using environment variables

                if platform == "instagram":
                    collection_name = config.MONGODB_ATLAS_COLLECTION_INSTAGRAM
                elif platform == "tiktok":
                    collection_name = config.MONGODB_ATLAS_COLLECTION_TIKTOK
                elif platform == "youtube":
                    collection_name = config.MONGODB_ATLAS_COLLECTION_YOUTUBE
                else:
                    continue

                if not collection_name:
                    continue

                platform_collection = db.get_collection(collection_name)

                try:
                    influencer = await platform_collection.find_one(
                        {"_id": ObjectId(rejected_id)}
                    )
                    if influencer:
                        influencer["_id"] = str(influencer["_id"])
                        influencer["platform"] = platform
                        # Remove embedding field to reduce payload size
                        if "embedding" in influencer:
                            del influencer["embedding"]
                        rejected_by_user_details.append(influencer)
                        found = True
                        break
                except Exception:
                    continue

            if not found:
                missing_rejected_by_user_influencers.append(
                    {
                        "id": rejected_id,
                        "reason": "Rejected by user influencer not found in any platform",
                    }
                )

        # Populate user details
        user_id = campaign.get("user_id")
        user_details = None
        if user_id:
            user_details = await _populate_user_details(user_id)

        # Populate approved influencer IDs with full details
        approved_ids = campaign.get("influencer_ids", [])
        approved_influencers_full = []
        if approved_ids:
            # Get platform from influencer_references if available
            if influencer_references:
                for ref in influencer_references:
                    inf_id = ref.get("influencer_id")
                    platform = ref.get("platform")
                    if inf_id in approved_ids:
                        details = await _populate_influencer_details([inf_id], platform)
                        if details:
                            approved_influencers_full.extend(details)
            else:
                # Try all platforms
                approved_influencers_full = await _populate_influencer_details(
                    approved_ids
                )

        # Populate generated influencer IDs with full details
        generated_ids = campaign.get("generated_influencers", [])
        generated_influencers_full = []
        if generated_ids and len(generated_ids) > 0:
            # Check if it's list of IDs (new format) or list of objects (legacy format)
            if isinstance(generated_ids[0], str):
                # New format: list of IDs, populate full details
                generated_influencers_full = await _populate_influencer_details(
                    generated_ids
                )
            else:
                # Legacy format: already full objects, return as is (remove embeddings)
                for inf in generated_ids:
                    if isinstance(inf, dict):
                        # Remove embedding if present
                        if "embedding" in inf:
                            inf_copy = inf.copy()
                            del inf_copy["embedding"]
                            generated_influencers_full.append(inf_copy)
                        else:
                            generated_influencers_full.append(inf)

        return {
            "campaign": campaign,
            "user_details": user_details,
            "approved_influencers": approved_influencers_full,
            "rejected_influencers": rejected_influencer_details,
            "rejected_by_user_influencers": rejected_by_user_details,
            "generated_influencers": generated_influencers_full,
            "total_approved": len(approved_influencers_full),
            "total_rejected": len(rejected_influencer_details),
            "total_rejected_by_user": len(rejected_by_user_details),
            "total_generated": len(generated_influencers_full),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in get_campaign_by_id: {str(e)}"
        ) from e


async def AdminApprovedSingleInfluencer(
    request_data: CampaignInfluencersRequest,
):
    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        existing = await collection.find_one(
            {
                "campaign_id": ObjectId(request_data.campaign_id),
                "influencer_id": ObjectId(request_data.influencer_id),
                "platform": request_data.platform,
            }
        )
        update_fields = {
            "username": request_data.username,
            "picture": request_data.picture,
            "engagementRate": request_data.engagementRate,
            "bio": request_data.bio,
            "followers": request_data.followers,
            "country": request_data.country,
            "status": request_data.status.value,
            "admin_approved": True,
        }
        if existing:
            await collection.update_one(
                {
                    "campaign_id": ObjectId(request_data.campaign_id),
                    "influencer_id": ObjectId(request_data.influencer_id),
                    "platform": request_data.platform,
                },
                {"$set": update_fields},
            )
        else:
            update_fields.update(
                {
                    "campaign_id": ObjectId(request_data.campaign_id),
                    "influencer_id": ObjectId(request_data.influencer_id),
                    "platform": request_data.platform,
                    "company_approved": False,
                }
            )
            await collection.insert_one(update_fields)

        return {"message": "Influencer approved successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error approving influencer: {str(e)}"
        )


async def user_reject_influencers(
    campaign_id: str, influencer_ids: List[str], user_id: str
) -> Dict[str, Any]:
    try:
        if not influencer_ids:
            return {"message": "No influencer IDs provided"}
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        if campaign.get("user_id") != user_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to modify this campaign",
            )

        # Get current approved influencer IDs and references
        current_influencer_ids = campaign.get("influencer_ids", [])
        current_references = campaign.get("influencer_references", [])
        current_rejected_by_user = campaign.get("rejectedByUser", [])

        # Validate that all influencer_ids are actually approved
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

        # Remove rejected influencers from approved lists
        for inf_id in current_influencer_ids:
            if inf_id not in influencer_ids:
                remaining_approved_ids.append(inf_id)

        for ref in current_references:
            if ref.get("influencer_id") not in influencer_ids:
                remaining_references.append(ref)

        # Update campaign
        result = await campaigns_collection.update_one(
            {"_id": ObjectId(campaign_id)},
            {
                "$set": {
                    "influencer_ids": remaining_approved_ids,
                    "influencer_references": remaining_references,
                    "rejectedByUser": current_rejected_by_user,
                    "updated_at": datetime.utcnow(),
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
        print(f"Error in user_reject_influencers: {str(e)}")
        return {"error": str(e)}


async def add_rejected_influencers(
    campaign_id: str, rejected_ids: List[str]
) -> Dict[str, Any]:
    """Append rejected influencer IDs to the campaign and update timestamp"""
    try:
        if not rejected_ids:
            return {"message": "No rejected ids provided"}
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        # Ensure campaign exists
        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        existing_rejected: List[str] = campaign.get("rejected_ids", []) or []
        # Deduplicate while preserving order (new first then existing)
        combined = list(dict.fromkeys(existing_rejected + rejected_ids))

        result = await campaigns_collection.update_one(
            {"_id": ObjectId(campaign_id)},
            {"$set": {"rejected_ids": combined, "updated_at": datetime.utcnow()}},
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=500, detail="Failed to update campaign with rejected ids"
            )

        return {
            "message": "Rejected influencers recorded",
            "total_rejected": len(combined),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in add rejected influencers: {str(e)}"
        ) from e


async def admin_generate_influencers(
    campaign_id: str, request_data: AdminGenerateInfluencersRequest
) -> Dict[str, Any]:
    """Admin generates influencers for a campaign"""
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        campaign_limit = campaign.get("limit") or request_data.limit or 10
        influencer_request = FindInfluencerRequest(
            campaign_id=campaign_id,
            user_id=campaign.get("user_id", ""),
            limit=campaign_limit,
        )

        result = await find_influencers_by_campaign(influencer_request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error in admin generate influencers: {str(e)}"
        ) from e


async def update_campaign_status(
    request_data: CampaignStatusUpdateRequest,
) -> Dict[str, Any]:
    """Update campaign status"""
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
            raise HTTPException(
                status_code=404, detail="Campaign not found or no changes made"
            )

        return {
            "message": f"Campaign status updated to {request_data.status}",
            "campaign_id": request_data.campaign_id,
            "status": request_data.status,
        }

    except Exception as e:
        print(f"Error in update_campaign_status: {str(e)}")
        return {"error": str(e)}


async def get_campaign_generated_influencers(campaign_id: str) -> Dict[str, Any]:
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        campaign = await campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

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
        raise HTTPException(
            status_code=500,
            detail=f"Error in get campaign generated influencers: {str(e)}",
        ) from e


async def reject_and_regenerate_influencers(request_data) -> Dict[str, Any]:
    """Reject influencers and generate new ones"""
    try:
        db = get_db()
        campaigns_collection = db.get_collection("campaigns")
        # Get campaign
        campaign = await campaigns_collection.find_one(
            {"_id": ObjectId(request_data.campaign_id)}
        )
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Get existing rejected IDs (both admin rejected and user rejected)
        existing_rejected = set(campaign.get("rejected_ids", []))
        existing_rejected_by_user = set(campaign.get("rejectedByUser", []))

        # Add new rejected IDs
        new_rejected_ids = list(set(request_data.influencer_ids))
        existing_rejected.update(new_rejected_ids)

        # Combine all rejected IDs for exclusion
        all_rejected_ids = existing_rejected | existing_rejected_by_user

        # Update campaign with rejected IDs
        await campaigns_collection.update_one(
            {"_id": ObjectId(request_data.campaign_id)},
            {
                "$set": {
                    "rejected_ids": list(existing_rejected),
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        # Use limit from campaign if available, otherwise use request limit
        campaign_limit = campaign.get("limit") or request_data.limit or 10

        # Create influencer search request with exclude_ids
        influencer_request = FindInfluencerRequest(
            campaign_id=request_data.campaign_id,
            user_id=campaign.get("user_id", ""),
            limit=campaign_limit,  # Use limit from campaign
            exclude_ids=list(
                all_rejected_ids
            ),  # Exclude all rejected IDs (both admin and user rejected)
        )

        # Generate new influencers
        result = await find_influencers_by_campaign(influencer_request)

        print(f"Result from find_influencers_by_campaign (regenerate): {result}")

        if "error" in result:
            return result

        # Get new influencers
        new_influencers = result.get("influencers", [])
        print(f"New influencers count: {len(new_influencers)}")

        # Get existing generated influencer IDs (now stored as simple list of IDs)
        existing_generated_ids = set()
        existing_generated = campaign.get("generated_influencers", [])

        # Check if it's list of IDs (new format) or list of objects (legacy format)
        if existing_generated and isinstance(existing_generated[0], str):
            # New format: list of IDs
            existing_generated_ids = set(existing_generated)
        else:
            # Legacy format: list of objects, extract IDs
            for inf in existing_generated:
                inf_id = inf.get("influencer_id") or inf.get("_id") or inf.get("id")
                if inf_id:
                    existing_generated_ids.add(str(inf_id))

        # Get IDs of already approved influencers (to exclude from regeneration results)
        already_approved_ids = set(campaign.get("influencer_ids", []))

        # Filter out already generated influencers AND already approved influencers
        final_new_influencers = []
        final_new_influencer_ids = []
        for inf in new_influencers:
            inf_id = inf.get("influencer_id") or inf.get("_id") or inf.get("id")
            inf_id_str = str(inf_id) if inf_id else None

            # Only include if not already generated AND not already approved
            if (
                inf_id_str
                and inf_id_str not in existing_generated_ids
                and inf_id_str not in already_approved_ids
            ):
                final_new_influencers.append(inf)
                final_new_influencer_ids.append(inf_id_str)

        # Limit to the requested number of new influencers
        final_new_influencers = final_new_influencers[:campaign_limit]
        final_new_influencer_ids = final_new_influencer_ids[:campaign_limit]

        # Combine with existing generated influencers (as IDs)
        all_generated_ids = existing_generated_ids | set(final_new_influencer_ids)

        # Update campaign with merged generated influencer IDs only (not full objects)
        await campaigns_collection.update_one(
            {"_id": ObjectId(request_data.campaign_id)},
            {
                "$set": {
                    "generated_influencers": list(all_generated_ids),  # Store only IDs
                    "status": CampaignStatus.PROCESSING,
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )

        return {
            "message": f"Rejected {len(new_rejected_ids)} influencer(s) and generated {len(final_new_influencers)} new influencer(s)",
            "campaign_id": request_data.campaign_id,
            "rejected_count": len(new_rejected_ids),
            "new_generated_count": len(final_new_influencers),
            "total_generated": len(all_generated_ids),
            "total_rejected": len(existing_rejected),
            "total_rejected_by_user": len(existing_rejected_by_user),
            "rejected_influencer_ids": new_rejected_ids,
            "new_influencers": final_new_influencers,
            "campaign": {
                "name": campaign["name"],
                "status": "processing",
                "platform": campaign.get("platform", []),
                "category": campaign.get("category", []),
            },
        }

    except Exception as e:
        print(f"Error in reject_and_regenerate_influencers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in reject and regenerate influencers: {str(e)}",
        ) from e


async def company_approved_campaign_influencers(
    page: int = 1,
    page_size: int = 10,
):
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=400, detail="Invalid pagination parameters")
    try:
        db = get_db()
        collection = db.get_collection("campaign_influencers")
        cursor = collection.find(
            {
                "admin_approved": True,
                "company_approved": True,
                "status": CampaignInfluencerStatus.APPROVED.value,
            }
        ).sort("updated_at", -1)

        cursor = cursor.skip((page - 1) * page_size).limit(page_size)
        influencers = await cursor.to_list(length=page_size)
        influencers = [convert_objectid(doc) for doc in influencers]
        total = await collection.count_documents(
            {
                "admin_approved": True,
                "company_approved": True,
                "status": CampaignInfluencerStatus.APPROVED.value,
            }
        )
        total_pages = (total + page_size - 1) // page_size
        return {
            "influencers": influencers,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in company approved campaign influencers: {str(e)}",
        ) from e

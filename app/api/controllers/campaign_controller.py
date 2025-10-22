from typing import Dict, Any, List
from datetime import datetime
from bson import ObjectId
from app.models.campaign_model import CreateCampaignRequest, CampaignResponse, ApproveSingleInfluencerRequest, CampaignListResponse
from app.services.embedding_service import connect_to_mongodb, sync_db



async def create_campaign(request_data: CreateCampaignRequest) -> Dict[str, Any]:
    """Create a new campaign"""
    try:
        await connect_to_mongodb()
        
        # Generate default name if not provided
        campaign_name = request_data.name
        if not campaign_name:
            campaign_name = f"Campaign - {', '.join(request_data.category)} - {', '.join(request_data.platform)}"
        
        campaign_doc = {
            "name": campaign_name,
            "description": request_data.description,
            "platform": request_data.platform,
            "category": request_data.category,
            "followers": request_data.followers,
            "country": request_data.country,
            "influencer_ids": request_data.influencer_ids,  # Legacy field
            "influencer_references": [],  # New field with platform info
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert into campaigns collection
        from app.services.embedding_service import sync_db
        # Ensure database connection is established
        if sync_db is None:
            await connect_to_mongodb()
        campaigns_collection = sync_db["campaigns"]
        result = campaigns_collection.insert_one(campaign_doc)
        
        return {
            "campaign_id": str(result.inserted_id),
            "message": "Campaign created successfully"
        }
        
    except Exception as e:
        print(f"Error in create_campaign: {str(e)}")
        return {"error": str(e)}


async def get_all_campaigns() -> Dict[str, Any]:
    """Get all campaigns"""
    try:
        await connect_to_mongodb()
        
        # Get the database connection after ensuring it's established
        from app.services.embedding_service import sync_db
        campaigns_collection = sync_db["campaigns"]
        
        campaigns = list(campaigns_collection.find().sort("created_at", -1))
        
        # Convert ObjectId to string and format response
        formatted_campaigns = []
        for campaign in campaigns:
            campaign["_id"] = str(campaign["_id"])
            formatted_campaigns.append(campaign)
        
        return {
            "campaigns": formatted_campaigns,
            "total": len(formatted_campaigns)
        }
        
    except Exception as e:
        print(f"Error in get_all_campaigns: {str(e)}")
        return {"error": str(e)}


async def get_campaign_by_id(campaign_id: str) -> Dict[str, Any]:
    """Get campaign details by ID with populated influencer data"""
    try:
        await connect_to_mongodb()
        
        # Get the database connection after ensuring it's established
        from app.services.embedding_service import sync_db
        campaigns_collection = sync_db["campaigns"]
        
        # Get campaign
        campaign = campaigns_collection.find_one({"_id": ObjectId(campaign_id)})
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
                    missing_influencers.append({"id": influencer_id, "reason": "Missing ID or platform"})
                    continue
                
                # Get collection name for platform using environment variables
                import os
                if platform == "instagram":
                    collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_INSTGRAM")
                elif platform == "tiktok":
                    collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_TIKTOK")
                elif platform == "youtube":
                    collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_YOUTUBE")
                else:
                    missing_influencers.append({"id": influencer_id, "platform": platform, "reason": "Invalid platform"})
                    continue
                
                if not collection_name:
                    missing_influencers.append({"id": influencer_id, "platform": platform, "reason": f"Collection name not configured for platform {platform}"})
                    continue
                
                platform_collection = sync_db[collection_name]
                print(f"Looking for influencer {influencer_id} in collection {collection_name}")
                
                try:
                    influencer = platform_collection.find_one({"_id": ObjectId(influencer_id)})
                    if influencer:
                        influencer["_id"] = str(influencer["_id"])
                        influencer["platform"] = platform
                        # Remove embedding field to reduce payload size
                        if "embedding" in influencer:
                            del influencer["embedding"]
                        influencer_details.append(influencer)
                    else:
                        missing_influencers.append({"id": influencer_id, "platform": platform, "reason": "Influencer not found"})
                except Exception as e:
                    missing_influencers.append({"id": influencer_id, "platform": platform, "reason": f"Invalid ID format: {str(e)}"})
        else:
            # Legacy format: search all platforms (less efficient)
            for influencer_id in campaign.get("influencer_ids", []):
                found = False
                for platform in ["instagram", "tiktok", "youtube"]:
                    # Get collection name using environment variables
                    if platform == "instagram":
                        collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_INSTGRAM")
                    elif platform == "tiktok":
                        collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_TIKTOK")
                    elif platform == "youtube":
                        collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_YOUTUBE")
                    else:
                        continue
                    
                    if not collection_name:
                        continue
                        
                    platform_collection = sync_db[collection_name]
                    
                    try:
                        influencer = platform_collection.find_one({"_id": ObjectId(influencer_id)})
                        if influencer:
                            influencer["_id"] = str(influencer["_id"])
                            influencer["platform"] = platform
                            # Remove embedding field to reduce payload size
                            if "embedding" in influencer:
                                del influencer["embedding"]
                            influencer_details.append(influencer)
                            found = True
                            break
                    except Exception as e:
                        continue
                
                if not found:
                    missing_influencers.append({"id": influencer_id, "reason": "Influencer not found in any platform"})
        
        return {
            "campaign": campaign,
            "influencers": influencer_details,
            "missing_influencers": missing_influencers,
            "total_found": len(influencer_details),
            "total_missing": len(missing_influencers)
        }
        
    except Exception as e:
        print(f"Error in get_campaign_by_id: {str(e)}")
        return {"error": str(e)}


async def approve_single_influencer(request_data: ApproveSingleInfluencerRequest) -> Dict[str, Any]:
    """Approve a single influencer and add to campaign with platform validation"""
    try:
        await connect_to_mongodb()
        
        # Get the database connection after ensuring it's established
        from app.services.embedding_service import sync_db
        campaigns_collection = sync_db["campaigns"]


        
        # Get current campaign
        campaign = campaigns_collection.find_one({"_id": ObjectId(request_data.campaign_id)})
        if not campaign:
            return {"error": "Campaign not found"}
        
        # Validate influencer exists in the specified platform
        import os
        if request_data.platform == "instagram":
            collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_INSTGRAM")
        elif request_data.platform == "tiktok":
            collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_TIKTOK")
        elif request_data.platform == "youtube":
            collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_YOUTUBE")
        else:
            return {"error": "Invalid platform"}
        
        if not collection_name:
            return {"error": f"Collection name not configured for platform {request_data.platform}"}
        
        platform_collection = sync_db[collection_name]
        
        print(f"Validating influencer {request_data.influencer_id} in collection {collection_name}")
        
        try:
            influencer = platform_collection.find_one({"_id": ObjectId(request_data.influencer_id)})
            print(f"Influencer found: {influencer is not None}")
            if not influencer:
                # Try to find by other fields as fallback
                influencer_by_username = platform_collection.find_one({"username": request_data.influencer_id})
                influencer_by_handle = platform_collection.find_one({"handle": request_data.influencer_id})
                if influencer_by_username or influencer_by_handle:
                    return {"error": f"Influencer found but with different ID format. Please use the correct ObjectId."}
                return {"error": f"Influencer not found in {request_data.platform} platform (collection: {collection_name})"}
        except Exception as e:
            return {"error": f"Invalid influencer ID format: {str(e)}"}
        
        # Get current influencer references
        current_references = campaign.get("influencer_references", [])
        current_influencer_ids = campaign.get("influencer_ids", [])  # Legacy field
        
        # Check if influencer already exists (check both new and legacy formats)
        if request_data.influencer_id in current_influencer_ids:
            return {"message": "Influencer already approved for this campaign"}
        
        # Check in new format
        for ref in current_references:
            if ref.get("influencer_id") == request_data.influencer_id:
                return {"message": "Influencer already approved for this campaign"}
        
        # Add new influencer reference
        new_reference = {
            "influencer_id": request_data.influencer_id,
            "platform": request_data.platform
        }
        new_references = current_references + [new_reference]
        new_influencer_ids = current_influencer_ids + [request_data.influencer_id]  # Legacy field
        
        # Update campaign with both formats
        result = campaigns_collection.update_one(
            {"_id": ObjectId(request_data.campaign_id)},
            {
                "$set": {
                    "influencer_ids": new_influencer_ids,  # Legacy field
                    "influencer_references": new_references,  # New field
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            return {"error": "Failed to update campaign"}
        
        return {
            "message": "Successfully added influencer to campaign",
            "influencer_id": request_data.influencer_id,
            "platform": request_data.platform,
            "total_influencers": len(new_influencer_ids)
        }
        
    except Exception as e:
        print(f"Error in approve_single_influencer: {str(e)}")
        return {"error": str(e)}

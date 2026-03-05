from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, UploadFile
from agents import Runner, Agent
from app.Guardails.CampaignCreation.campaignInput_guardrails import (
    CampaignCreationInputGuardrail,
)
from app.Guardails.CampaignCreation.campaignoutput_guardrails import (
    CampaignCreationOutputGuardrail,
)
from typing import Dict
from app.Schemas.campaign_influencers import (
    CampaignBriefDBResponse,
    CampaignBriefResponse,
    UpdateCampaignBriefRequest,
)
from datetime import datetime, timezone
from app.model.Campaign.campaignbrief_model import (
    CampaignBriefGeneration,
    CampaignBriefStatus,
)
from app.utils.prompts import CREATECAMPAIGNBREAKDOWN_PROMPT
from app.db.connection import get_db
from agents.exceptions import InputGuardrailTripwireTriggered
import json
from app.utils.image_generator import generate_campaign_logo, s3_client
from app.config.credentials_config import config
import uuid


async def validate_user(user_id: str):
    db = get_db()
    user = await db.get_collection("users").find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def store_campaign_brief(
    prompt: str,
    response: CampaignBriefResponse,
    user_doc: dict,
    regenerated_from: Optional[str] = None,
) -> CampaignBriefGeneration:
    try:
        db = get_db()
        collection = db.get_collection("CampaignBriefGeneration")
        user_id = str(user_doc["_id"])
        last_brief = await collection.find_one(
            {"user_id": user_id}, sort=[("version", -1)]
        )
        next_version = 1 if not last_brief else last_brief.get("version", 0) + 1
        document = CampaignBriefGeneration(
            user_id=user_id,
            prompt=prompt,
            response=response,
            status=(
                CampaignBriefStatus.REGENERATED
                if regenerated_from
                else CampaignBriefStatus.GENERATED
            ),
            version=next_version,
            regenerated_from=regenerated_from,
        )
        await collection.insert_one(document.model_dump(by_alias=True))
        return document

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to store campaign brief: {str(e)}"
        )


async def create_campaign_brief(user_input: str, user_id: str) -> CampaignBriefResponse:
    user_doc = await validate_user(user_id)

    try:
        result = await Runner.run(
            Agent(
                name="create_campaign",
                instructions=CREATECAMPAIGNBREAKDOWN_PROMPT,
                input_guardrails=[CampaignCreationInputGuardrail],
                output_guardrails=[CampaignCreationOutputGuardrail],
                output_type=CampaignBriefResponse,
            ),
            input=user_input,
        )

        if isinstance(result.final_output, dict):
            response_obj = CampaignBriefResponse(**result.final_output)
        elif isinstance(result.final_output, CampaignBriefResponse):
            response_obj = result.final_output
        else:
            response_obj = CampaignBriefResponse(**json.loads(result.final_output))

        logo_url = await generate_campaign_logo(
            title=response_obj.title,
            overview=" ".join(response_obj.campaign_overview),
            brand_name_influencer_campaign_brief=response_obj.brand_name_influencer_campaign_brief,
        )
        response_obj.campaign_logo_url = logo_url

        stored_doc = await store_campaign_brief(
            prompt=user_input,
            response=response_obj,
            user_doc=user_doc,
        )

        response_obj.id = stored_doc.id
        return response_obj

    except InputGuardrailTripwireTriggered:
        raise HTTPException(status_code=400, detail="Invalid campaign request.")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Campaign generation failed: {str(e)}"
        )


async def delete_campaign_brief_service(brief_id: str):
    db = get_db()
    collection = db.get_collection("CampaignBriefGeneration")

    existing = await collection.find_one({"_id": brief_id})

    if not existing:
        raise HTTPException(status_code=404, detail="Campaign brief not found")

    await collection.delete_one({"_id": brief_id})

    return {"message": "Campaign brief deleted successfully"}


async def update_campaign_brief_service(
    brief_id: str, update_request: UpdateCampaignBriefRequest
) -> CampaignBriefResponse:

    db = get_db()
    collection = db.get_collection("CampaignBriefGeneration")

    existing_brief = await collection.find_one({"_id": brief_id})
    if not existing_brief:
        raise HTTPException(status_code=404, detail="Campaign brief not found")

    update_data = {k: v for k, v in update_request.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    await collection.update_one(
        {"_id": brief_id},
        {"$set": {f"response.{k}": v for k, v in update_data.items()}},
    )

    updated_brief = await collection.find_one({"_id": brief_id})
    response_obj = CampaignBriefResponse(**updated_brief["response"])
    response_obj.id = str(updated_brief["_id"])

    return response_obj


async def get_campaign_briefs(
    user_id: str, skip: int = 0, limit: int = 10
) -> List[CampaignBriefDBResponse]:

    user_doc = await validate_user(user_id)
    db = get_db()
    collection = db.get_collection("CampaignBriefGeneration")

    cursor = (
        collection.find({"user_id": str(user_doc["_id"])})
        .sort("version", -1)
        .skip(skip)
        .limit(limit)
    )

    briefs = []

    async for doc in cursor:
        response_data = doc.get("response", {})
        if "title" not in response_data or not response_data.get("title"):
            response_data["title"] = "Untitled Campaign"

        try:
            response_obj = CampaignBriefResponse(**response_data)
        except Exception as e:
            print(f"CampaignBrief parsing error: {e}")
            continue

        briefs.append(
            CampaignBriefDBResponse(
                id=str(doc["_id"]),
                user_id=doc["user_id"],
                prompt=doc["prompt"],
                response=response_obj,
                status=doc["status"],
                version=doc["version"],
                regenerated_from=doc.get("regenerated_from"),
                created_at=doc.get("created_at"),
            )
        )

    return briefs


async def get_campaign_brief_by_id(campaign_id: str):
    db = get_db()
    collection = db.get_collection("CampaignBriefGeneration")

    campaign = await collection.find_one({"_id": campaign_id})

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign brief not found")

    response_data = campaign.get("response", {})
    if "title" not in response_data or not response_data.get("title"):
        response_data["title"] = "Untitled Campaign"

    try:
        response_obj = CampaignBriefResponse(**response_data)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Corrupted campaign brief data: {str(e)}"
        )

    return CampaignBriefDBResponse(
        id=str(campaign["_id"]),
        user_id=campaign["user_id"],
        prompt=campaign["prompt"],
        response=response_obj,
        status=campaign["status"],
        version=campaign["version"],
        regenerated_from=campaign.get("regenerated_from"),
        created_at=campaign.get("created_at"),
    )


async def update_campaign_brief_logo_service(
    brief_id: str, file: UploadFile
) -> CampaignBriefDBResponse:
    """
    Replace the auto-generated campaign logo with a user-uploaded image.
    - Validates and reads the uploaded file
    - Deletes any existing logo from S3 (best-effort)
    - Uploads the new logo to S3 with a fresh key
    - Updates response.campaign_logo_url in CampaignBriefGeneration
    - Returns the updated brief document
    """
    print(f"[update_campaign_brief_logo_service] Starting logo update for brief_id={brief_id}")

    file_bytes = await _validate_and_read_logo_file(file)

    db = get_db()
    collection = db.get_collection("CampaignBriefGeneration")

    existing_brief = await collection.find_one({"_id": brief_id})
    if not existing_brief:
        print(f"[update_campaign_brief_logo_service] No brief found for _id={brief_id}")
        raise HTTPException(status_code=404, detail="Campaign brief not found")

    existing_logo_url = (existing_brief.get("response") or {}).get("campaign_logo_url")
    _delete_old_logo_if_exists(existing_logo_url)

    new_logo_url = await _upload_new_logo_to_s3(
        brief_id=brief_id,
        file=file,
        file_bytes=file_bytes,
        previous_logo_url=existing_logo_url,
    )

    update_result = await collection.update_one(
        {"_id": brief_id},
        {
            "$set": {
                "response.campaign_logo_url": new_logo_url,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    print(
        "[update_campaign_brief_logo_service] Mongo update result: "
        f"matched_count={update_result.matched_count}, modified_count={update_result.modified_count}"
    )

    updated = await get_campaign_brief_by_id(brief_id)
    print(
        "[update_campaign_brief_logo_service] Updated brief response.campaign_logo_url="
        f"{updated.response.campaign_logo_url}"
    )
    return updated


async def _validate_and_read_logo_file(file: UploadFile) -> bytes:
    if file.content_type not in ["image/png", "image/jpeg"]:
        print(
            f"[update_campaign_brief_logo_service] Invalid content_type={file.content_type}"
        )
        raise HTTPException(
            status_code=400,
            detail="Only PNG or JPEG images are allowed",
        )

    file_bytes = await file.read()
    if not file_bytes:
        print("[update_campaign_brief_logo_service] Empty file uploaded")
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    return file_bytes


def _delete_old_logo_if_exists(existing_logo_url: Optional[str]) -> None:
    prefix = (
        f"https://{config.S3_BUCKET_NAME}.s3."
        f"{config.AWS_REGION}.amazonaws.com/"
    )

    if existing_logo_url and existing_logo_url.startswith(prefix):
        old_key = existing_logo_url[len(prefix) :]
        print(
            "[update_campaign_brief_logo_service] Deleting old S3 logo object: "
            f"{old_key} (existing_logo_url={existing_logo_url})"
        )
        try:
            s3_client.delete_object(
                Bucket=config.S3_BUCKET_NAME,
                Key=old_key,
            )
        except Exception as e:
            # Log but do not fail the whole operation if delete fails
            print(
                "[update_campaign_brief_logo_service] Failed to delete old logo from S3: "
                f"{e}"
            )


async def _upload_new_logo_to_s3(
    brief_id: str,
    file: UploadFile,
    file_bytes: bytes,
    previous_logo_url: Optional[str],
) -> str:
    prefix = (
        f"https://{config.S3_BUCKET_NAME}.s3."
        f"{config.AWS_REGION}.amazonaws.com/"
    )

    extension = file.filename.split(".")[-1].lower()
    unique_id = str(uuid.uuid4())
    s3_key = f"campaign_logos/{brief_id}_{unique_id}.{extension}"
    print(
        "[update_campaign_brief_logo_service] Using new S3 key for uploaded logo: "
        f"{s3_key} (previous_logo_url={previous_logo_url})"
    )

    try:
        s3_client.put_object(
            Bucket=config.S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_bytes,
            ContentType=file.content_type,
        )
    except Exception as e:
        print(f"[update_campaign_brief_logo_service] S3 upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")

    logo_url = prefix + s3_key
    print(
        "[update_campaign_brief_logo_service] Uploaded new logo to S3 "
        f"Bucket={config.S3_BUCKET_NAME}, Key={s3_key}, url={logo_url}"
    )
    return logo_url

from datetime import datetime
from bson.objectid import ObjectId
from app.Schemas.whatsappconversation import WhatsappConversationMessage
from app.config.credentials_config import config
from app.core.exception import (
    BadRequestException,
    InternalServerErrorException,
    NotFoundException,
)
from app.db.connection import get_db
from typing import Dict, Any, Optional

from app.Schemas.user_model import UserResponse, UserRole, UserStatus
from app.utils.helpers import convert_objectid


async def get_all_users(page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    try:
        db = get_db()
        users_collection = db.get_collection("users")
        user = (
            await users_collection.find({"role": UserRole.COMPANY.value})
            .sort("created_at", -1)
            .skip((page - 1) * page_size)
            .limit(page_size)
            .to_list(length=page_size)
        )
        user = [convert_objectid(doc) for doc in user]
        user_response = [
            UserResponse(
                user_id=str(user["_id"]),
                company_name=user["company_name"],
                email=user["email"],
                contact_person=user["contact_person"],
                phone=user["phone"],
                role=UserRole(user["role"]),
                status=UserStatus(user["status"]),
                created_at=user["created_at"],
                updated_at=user["updated_at"],
            ).model_dump()
            for user in user
        ]
        total = await users_collection.count_documents({"role": UserRole.COMPANY.value})
        total_pages = (total + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        return {
            "status_code": 200,
            "message": "Users retrieved successfully",
            "users": user_response,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
        }
    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error retrieving users: {str(e)}"
        ) from e


async def update_user_status(user_id: str, status: str) -> Dict[str, Any]:
    try:
        db = get_db()
        users_collection = db.get_collection("users")

        if status not in [
            UserStatus.ACTIVE.value,
            UserStatus.INACTIVE.value,
            UserStatus.SUSPENDED.value,
        ]:
            raise BadRequestException(message="Invalid status")

        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"status": status}}
        )

        if result.matched_count == 0:
            raise NotFoundException(message="User not found")

        updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
        updated_user = convert_objectid(updated_user)
        updated_user_response = UserResponse(
            user_id=str(updated_user["_id"]),
            company_name=updated_user["company_name"],
            email=updated_user["email"],
            contact_person=updated_user["contact_person"],
            phone=updated_user["phone"],
            role=UserRole(updated_user["role"]),
            status=UserStatus(updated_user["status"]),
        ).model_dump()
        return {
            "status_code": 200,
            "message": "User status updated successfully",
            "user": updated_user_response,
        }

    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error updating user status: {str(e)}"
        )


async def Whatsapp_Users_Sessions_management(
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    try:
        db = get_db()
        collection = db.get_collection(
            config.MONGODB_ATLAS_COLLECTION_WHATSAPP_SESSIONS
        )
        skip = (page - 1) * page_size
        cursor = collection.find().sort("last_active", -1).skip(skip).limit(page_size)
        users = await cursor.to_list(length=page_size)
        users = [convert_objectid(user) for user in users]

        user_response = []
        for user in users:
            user_response.append(
                {
                    "id": user.get("_id"),
                    "thread_id": user.get("thread_id"),
                    "name": user.get("name"),
                    "last_message": user.get("user_message") or user.get("reply"),
                    "last_active": user.get("last_active"),
                    "platform": user.get("platform", []),
                    "ready_for_campaign": user.get("ready_for_campaign", False),
                    "campaign_created": user.get("campaign_created", False),
                    "acknowledged": user.get("acknowledged", False),
                    "conversation_round": user.get("conversation_round", 0),
                    "status": (
                        "COMPLETED"
                        if user.get("done")
                        else "WAITING" if user.get("reply_sent") else "ACTIVE"
                    ),
                }
            )
        total = await collection.count_documents({})
        total_pages = (total + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "users": user_response,
        }

    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error retrieving whatsapp users: {str(e)}"
        ) from e


async def Whatsapp_messages_management(
    thread_id: str,
    page: int = 1,
    page_size: int = 20,
) -> Dict[str, Any]:
    try:
        db = get_db()
        collection = db.get_collection(config.MONGODB_COLLECTION_WHATSAPP_MESSAGES)
        skip = (page - 1) * page_size
        cursor = (
            collection.find({"thread_id": thread_id})
            .sort("timestamp", -1)
            .skip(skip)
            .limit(page_size)
        )
        messages = await cursor.to_list(length=page_size)
        messages = [convert_objectid(m) for m in messages]
        messages.reverse()

        total = await collection.count_documents({"thread_id": thread_id})
        total_pages = (total + page_size - 1) // page_size

        return {
            "messages": [
                WhatsappConversationMessage(
                    _id=message["_id"],
                    thread_id=message["thread_id"],
                    username=message["username"],
                    sender=message["sender"],
                    message=message["message"],
                    timestamp=message["timestamp"].isoformat(),
                )
                for message in messages
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error retrieving whatsapp messages: {str(e)}"
        ) from e


async def whatsapp_messages_cursor(
    thread_id: str,
    before: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    try:
        db = get_db()
        collection = db.get_collection("whatsapp_messages")
        query = {"thread_id": thread_id}

        if before:
            cursor_time = datetime.fromisoformat(before)
            query["timestamp"] = {"$lt": cursor_time}
        cursor = collection.find(query).sort("timestamp", -1).limit(limit + 1)

        docs = await cursor.to_list(length=limit + 1)
        has_more = len(docs) > limit
        docs = docs[:limit]
        docs.reverse()

        messages = [
            {
                "_id": str(d["_id"]),
                "thread_id": d["thread_id"],
                "username": d.get("username"),
                "sender": d["sender"],
                "message": d["message"],
                "timestamp": d["timestamp"].isoformat(),
            }
            for d in docs
        ]
        next_cursor = messages[0]["timestamp"] if has_more else None
        return {
            "messages": messages,
            "next_cursor": next_cursor,
            "has_more": has_more,
        }

    except Exception as e:
        raise InternalServerErrorException(
            message=f"Error retrieving whatsapp messages: {str(e)}"
        ) from e

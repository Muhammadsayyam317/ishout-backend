from app.db.mongo_session import get_session_collection


async def get_conversation_round(sender_id):
    session_collection = get_session_collection()
    state = await session_collection.find_one({"sender_id": sender_id})
    if state:
        return state.get("conversation_round", 0)
    return 0


async def increment_conversation_round(sender_id):
    session_collection = get_session_collection()
    result = await session_collection.find_one_and_update(
        {"sender_id": sender_id},
        {"$inc": {"conversation_round": 1}},
        upsert=True,
    )
    return result.get("conversation_round", 0) + 1 if result else 1


async def is_duplicate_message(redis, message_id: str, ttl=60):
    key = f"whatsapp:dedup:{message_id}"
    return not await redis.set(key, "1", ex=ttl, nx=True)


async def rate_limit(redis, sender_id, limit=10, window=60):
    key = f"rate:{sender_id}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, window)
    return count <= limit

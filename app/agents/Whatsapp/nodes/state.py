from app.db.mongo_session import get_session_collection
import redis.asyncio as redis
from app.config.credentials_config import config

redis_client = redis.from_url(config.REDIS_URL, decode_responses=True)


async def get_conversation_round(sender_id):
    print("Entering into get_conversation_round")
    print("--------------------------------")
    print(sender_id)
    print("--------------------------------")
    session_collection = get_session_collection()
    state = await session_collection.find_one({"sender_id": sender_id})
    if state:
        return state.get("conversation_round", 0)
    print("Conversation round not found")
    print("--------------------------------")
    print(0)
    print("--------------------------------")
    return 0


async def increment_conversation_round(sender_id):
    print("Entering into increment_conversation_round")
    print("--------------------------------")
    print(sender_id)
    print("--------------------------------")
    session_collection = get_session_collection()
    result = await session_collection.find_one_and_update(
        {"sender_id": sender_id},
        {"$inc": {"conversation_round": 1}},
        upsert=True,
    )
    print("Conversation round incremented")
    print("--------------------------------")
    print(result.get("conversation_round", 0) + 1 if result else 1)
    print("--------------------------------")
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


async def cleanup_old_checkpoints(thread_id: str, keep_round: int):
    print(f"Cleaning up old checkpoints for {thread_id} with keep_round {keep_round}")
    pattern = f"langgraph:checkpoint:{thread_id}-r*"
    keys = await redis_client.keys(pattern)

    for key in keys:
        if not key.endswith(f"-r{keep_round}"):
            await redis_client.delete(key)

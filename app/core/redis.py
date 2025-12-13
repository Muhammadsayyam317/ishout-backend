from redis.asyncio import Redis
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.agents.graph.whatsapp_graph import graph
from app.config.credentials_config import config


async def redis_checkpointer():
    redis = Redis.from_url(
        config.REDIS_URL,
        decode_responses=True,
    )

    checkpointer = AsyncRedisSaver(
        redis=redis,
        ttl=60 * 60 * 24,
        key_prefix="whatsapp:agent",
    )

    compiled = graph.compile(checkpointer=checkpointer)
    return compiled

from redis.asyncio import Redis
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.agents.graph.whatsapp_graph import graph
from app.config.credentials_config import config


async def redis_checkpointer():

    scheme = "rediss" if getattr(config, "REDIS_TLS", False) else "redis"

    if config.REDIS_USERNAME and config.REDIS_PASSWORD:
        redis_url = f"{scheme}://{config.REDIS_USERNAME}:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}"
        print(redis_url)
    elif config.REDIS_PASSWORD:
        redis_url = f"{scheme}://:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}"
        print(redis_url)
    else:
        redis_url = f"{scheme}://{config.REDIS_HOST}:{config.REDIS_PORT}"
        print(redis_url)

    redis = Redis.from_url(redis_url, decode_responses=True)

    checkpointer = AsyncRedisSaver(
        redis=redis,
        ttl=60 * 60 * 24,  # 24 hours
        key_prefix="whatsapp:agent",
    )

    compiled = graph.compile(checkpointer=checkpointer)
    return compiled

from redis.asyncio import Redis
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.agents.graph.whatsapp_graph import graph
from app.config.credentials_config import config


redis_url = f"redis://{config.REDIS_USERNAME}:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}"
redis_client = Redis.from_url(
    redis_url,
    decode_responses=True,
)

# Create checkpointer ONCE
checkpointer = AsyncRedisSaver(
    redis=redis_client,
    ttl=60 * 60 * 24,
    key_prefix="whatsapp:agent",
)

redis_checkpointer = graph.compile(checkpointer=checkpointer)

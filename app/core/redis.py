from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.agents.graph.whatsapp_graph import graph
from app.config.credentials_config import config

if (
    not config.REDIS_USERNAME
    or not config.REDIS_PASSWORD
    or not config.REDIS_HOST
    or not config.REDIS_PORT
):
    raise ValueError("Redis configuration is required")
redis_url = f"redis://{config.REDIS_USERNAME}:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}"
if not redis_url:
    raise ValueError("Redis URL is required")
# Create checkpointer ONCE
checkpointer = AsyncRedisSaver(
    url=redis_url,
    ttl=60 * 60 * 24,
    key_prefix="whatsapp:agent",
    retryDelayOnFailover=100,
    maxRetriesPerRequest=3,
)

redis_checkpointer = graph.compile(checkpointer=checkpointer)

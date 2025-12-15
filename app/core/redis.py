from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.agents.graph.whatsapp_graph import graph
from app.config.credentials_config import config

REDIS_URI = f"redis://{config.REDIS_USERNAME}:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}"
print(REDIS_URI)


async def init_redis_agent(app):
    if hasattr(app.state, "whatsapp_agent"):
        return

    contextmanager = AsyncRedisSaver.from_conn_string(
        REDIS_URI,
        ttl={"default_ttl": 60 * 60 * 24},
    )

    checkpointer = await contextmanager.__aenter__()
    app.state.whatsapp_agent = graph.compile(checkpointer=checkpointer)

    print("✅ WhatsApp agent initialized with Redis")

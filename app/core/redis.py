from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.agents.graph.whatsapp_graph import graph
from app.config.credentials_config import config


async def init_redis_agent(app):
    if hasattr(app.state, "whatsapp_agent"):
        return

    contextmanager = AsyncRedisSaver.from_conn_string(
        config.REDIS_URL,
        ttl={"default_ttl": 60},
    )

    checkpointer = await contextmanager.__aenter__()
    app.state.whatsapp_agent = graph.compile(checkpointer=checkpointer)

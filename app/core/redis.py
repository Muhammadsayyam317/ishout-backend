from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.agents.graph.whatsapp_graph import graph
from app.config.credentials_config import config

REDIS_URI = f"redis://{config.REDIS_USERNAME}:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}"

whatsapp_agent = None
checkpointer = None


async def init_redis_agent():
    global whatsapp_agent, checkpointer
    if whatsapp_agent is not None:
        return
    async with AsyncRedisSaver.from_conn_string(REDIS_URI) as checkpointer:
        await checkpointer.setup()
        whatsapp_agent = graph.compile(checkpointer=checkpointer)

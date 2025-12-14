from langgraph.checkpoint.redis import RedisSaver
from app.agents.graph.whatsapp_graph import graph
from app.config.credentials_config import config

REDIS_URI = f"redis://{config.REDIS_USERNAME}:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}"

whatsapp_agent = None


async def init_redis_agent():
    global whatsapp_agent
    with RedisSaver.from_conn_string(REDIS_URI) as checkpointer:
        checkpointer.setup()
        whatsapp_agent = graph.compile(checkpointer=checkpointer)

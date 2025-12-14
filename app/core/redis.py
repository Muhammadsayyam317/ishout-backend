from langgraph.checkpoint.redis import RedisSaver
from app.agents.graph.whatsapp_graph import graph
from app.config.credentials_config import config


REDIS_URI = f"redis://{config.REDIS_USERNAME}:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}"


async def redis_checkpointer():
    with RedisSaver.from_conn_string(REDIS_URI) as checkpointer:
        checkpointer.setup()
    compiled_graph = graph.compile(checkpointer=checkpointer)
    return compiled_graph

from langgraph.checkpoint.redis import RedisSaver
from app.agents.graph.whatsapp_graph import graph
from app.config.credentials_config import config

redis_url = f"redis://{config.REDIS_USERNAME}:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}"


async def redis_checkpointer():
    with RedisSaver.from_conn_string(redis_url) as checkpointer:
        checkpointer.setup()
    compiled_graph = graph.compile(checkpointer=checkpointer)
    return compiled_graph

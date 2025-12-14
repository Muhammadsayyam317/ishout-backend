from langgraph.checkpoint.redis import RedisSaver
from app.agents.graph.whatsapp_graph import graph
from app.config.credentials_config import config

redis_url = f"redis://{config.REDIS_USERNAME}:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}"

checkpointer = RedisSaver.from_conn_string(redis_url)
checkpointer.ttl = 60 * 60 * 24
checkpointer.key_prefix = "whatsapp:agent"


async def redis_checkpointer():
    await checkpointer.setup()
    compiled_graph = graph.compile(checkpointer=checkpointer)
    return compiled_graph

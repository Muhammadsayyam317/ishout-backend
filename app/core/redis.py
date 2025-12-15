from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.agents.graph.whatsapp_graph import graph
from app.config.credentials_config import config

REDIS_URI = f"redis://:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}"

whatsapp_agent = None
checkpointer_contextmanager = None


async def init_redis_agent():
    global whatsapp_agent, checkpointer_contextmanager
    if whatsapp_agent is not None:
        return

    # Create context manager
    checkpointer_contextmanager = AsyncRedisSaver.from_conn_string(
        REDIS_URI,
        ttl=60 * 60 * 24,
    )

    # enter into async context manager
    checkpointer = await checkpointer_contextmanager.__aenter__()
    whatsapp_agent = graph.compile(checkpointer=checkpointer)
    print("WhatsApp agent initialized with Redis")

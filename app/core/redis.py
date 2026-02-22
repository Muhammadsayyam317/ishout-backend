from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from app.agents.Whatsapp.graph.whatsapp_graph import graph
from app.agents.WhatsappNegotiation.graph.whatsappnegotiation_graph import (
    negotiation_graph,
)
from app.config.credentials_config import config
import redis.asyncio as redis
from app.utils.printcolors import Colors


async def Initialize_redis(app):
    if hasattr(app.state, "whatsapp_agent"):
        return

    contextmanager = AsyncRedisSaver.from_conn_string(
        config.REDIS_URL,
        ttl={"default_ttl": 86400},  # 1 day
    )
    checkpointer = await contextmanager.__aenter__()
    app.state.whatsapp_agent = graph.compile(checkpointer=checkpointer)
    print(f"{Colors.GREEN}Redis initialized successfully")
    print("--------------------------------")


async def initialize_negotiation_redis(app, graph):
    if hasattr(app.state, "whatsapp_negotiation_agent"):
        return
    contextmanager = AsyncRedisSaver.from_conn_string(
        config.REDIS_URL, ttl={"default_ttl": 300}
    )
    checkpointer = await contextmanager.__aenter__()
    app.state.whatsapp_negotiation_agent = graph.compile(checkpointer=checkpointer)
    print(f"{Colors.GREEN}Negotiation Redis initialized successfully")


async def redis_info():
    r = redis.from_url(config.REDIS_URL)
    info = await r.info("memory")
    return {
        "used_memory_mb": info["used_memory"] / (1024 * 1024),
        "keys": await r.dbsize(),
    }

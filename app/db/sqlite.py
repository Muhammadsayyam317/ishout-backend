import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.agents.nodes.graph import graph


async def build_whatsapp_agent():
    db = await aiosqlite.connect("whatsapp_agent.db")
    checkpointer = AsyncSqliteSaver(db)
    return graph.compile(checkpointer=checkpointer)

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.agents.nodes.graph import graph


async def build_whatsapp_agent(sqlite_path: str | None = "whatsapp_agent.db"):
    sqlite_db = await aiosqlite.connect(sqlite_path)
    checkpointer = AsyncSqliteSaver(sqlite_db)
    compiled = graph.compile(checkpointer=checkpointer)
    return compiled

import sqlite3
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from app.agents.nodes.graph import graph


async def build_whatsapp_agent():
    db = await aiosqlite.connect("whatsapp_agent.db")
    checkpointer = AsyncSqliteSaver(db)
    return graph.compile(checkpointer=checkpointer)


def create_tables():
    with sqlite3.connect("whatsapp_agent.db") as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS whatsapp_sessions (
            sender_id TEXT PRIMARY KEY,
            platform TEXT,
            country TEXT,
            category TEXT,
            number_of_influencers INTEGER,
            last_active INTEGER,
            created_at INTEGER,
            updated_at INTEGER
        );
        """
        )
        conn.commit()
    print("Tables created successfully")

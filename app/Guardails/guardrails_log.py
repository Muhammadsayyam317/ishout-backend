from app.db.connection import get_db


async def log_guardrail(payload: dict):
    db = get_db()
    await db.get_collection("guardrail_logs").insert_one(payload)

from app.db.connection import get_db
from app.config.credentials_config import config


async def log_guardrail(payload: dict):
    db = get_db()
    await db.get_collection(config.MONGODB_GUARDRAIL_LOGS).insert_one(payload)

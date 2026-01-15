from app.services.whatsapp.save_message import save_conversation_message
from app.utils.Enums.user_enum import SenderType


async def persist_user_message(*, thread_id: str, username: str, message: str):
    await save_conversation_message(
        thread_id=thread_id,
        username=username,
        sender=SenderType.USER.value,
        message=message,
    )

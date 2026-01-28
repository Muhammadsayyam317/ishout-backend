from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT


def build_message_context(last_messages: list[dict], latest: str) -> str:
    """
    Build conversation context for the AI reply.
    """

    history = "\n".join(
        f"{'AI' if msg.get('sender_type') == 'AI' else 'User'}: {msg.get('message', '')}"
        for msg in last_messages
    )

    return f"""
{NEGOTIATE_INFLUENCER_DM_PROMPT}

Conversation so far:
{history}

Latest message:
User: {latest}

Write the next reply as a natural human text message.
""".strip()


def normalize_ai_reply(reply) -> str:
    DEFAULT_REPLY = "Thanks for your message! Let me check and get back to you shortly."

    if isinstance(reply, GenerateReplyOutput):
        return reply.reply or DEFAULT_REPLY
    elif isinstance(reply, dict) and "reply" in reply:
        return reply["reply"] or DEFAULT_REPLY
    elif isinstance(reply, str):
        return reply or DEFAULT_REPLY
    else:
        return DEFAULT_REPLY

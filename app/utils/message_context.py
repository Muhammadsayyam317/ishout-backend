from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.utils.prompts import NEGOTIATE_INFLUENCER_DM_PROMPT


def build_message_context(last_messages: list[dict], latest: str) -> str:
    """
    Build the conversation context to provide to the AI.
    """
    history = ""
    for msg in last_messages:
        speaker = "AI" if msg["sender_type"] == "AI" else "User"
        history += f"{speaker}: {msg['message']}\n"

    return f"""{NEGOTIATE_INFLUENCER_DM_PROMPT}

Conversation so far:
{history}

Latest message:
User: {latest}

Write the next reply as a human would text.
"""


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

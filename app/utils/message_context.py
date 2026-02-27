from app.Schemas.instagram.message_schema import GenerateReplyOutput
from app.utils.prompts import (
    ANALYZE_INFLUENCER_WHATSAPP_PROMPT,
    NEGOTIATE_INFLUENCER_DM_PROMPT,
)


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


def build_whatsapp_message_context(last_messages: list[dict], latest: str) -> str:
    history = "\n".join(
        f"{'AI' if msg.get('sender_type') == 'AI' else 'User'}: {msg.get('message', '')}"
        for msg in last_messages
    )

    return f"""
{ANALYZE_INFLUENCER_WHATSAPP_PROMPT}

Conversation so far:
{history}

Latest message:
User: {latest}

Write the next reply as a natural WhatsApp message.
Keep it short, friendly, and human.
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


def get_history_list(state: dict) -> list:
    """
    Return state['history'] as a list. Never return a dict.
    Mongo or other storage may persist history in a shape that deserializes as a dict;
    passing that to agents or calling .append()/.extend() on it causes runtime errors.
    """
    h = state.get("history")
    if isinstance(h, list):
        return h
    return []


def set_history_list(state: dict, history: list) -> None:
    """Ensure state['history'] is a list so later setdefault/append are safe."""
    state["history"] = history if isinstance(history, list) else []


def history_to_agent_messages(history: list[dict]) -> list[dict]:
    """
    Convert our history (sender_type: 'USER'|'AI', message: str) to the format
    expected by the agents API: role 'user'|'assistant', content: str.
    """
    out = []
    for msg in history:
        if not isinstance(msg, dict):
            continue
        role = "user" if (msg.get("sender_type") or "").upper() == "USER" else "assistant"
        content = (msg.get("message") or msg.get("content") or "").strip()
        if content:
            out.append({"role": role, "content": content})
    return out

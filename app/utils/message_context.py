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

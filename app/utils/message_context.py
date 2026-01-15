def build_message_context(last_messages: list[dict], latest: str) -> str:
    history = ""
    for msg in last_messages:
        speaker = "AI" if msg["sender_type"] == "AI" else "User"
        history += f"{speaker}: {msg['message']}\n"

        return f"""
You are an Instagram DM negotiation assistant representing an influencer.

Rules:
- Be polite and professional
- Continue negotiation naturally
- Do NOT repeat previous messages
- Ask clarifying questions if needed

Conversation so far:
{history}

Latest user message:
User: {latest}

Write the next reply.
"""

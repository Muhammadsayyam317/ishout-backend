def instagram_fallback(reason: str) -> str:
    if reason == "escalate":
        return "Thanks for sharing the details. I’m reviewing this internally and will get back to you shortly."
    elif reason == "block":
        return "I'm sorry, but I can't process this request. Please try again later."
    elif reason == "ok":
        return "Thank you for your message. I'll get back to you shortly."


FALLBACK_RESPONSES = [
    "Thanks for reaching out. Could you share a bit more about the campaign so I can guide you properly?",
    "Thank you for your message. I'll get back to you shortly.",
    "Happy to explore this — just need a few details before moving forward.",
    "Let me check on this. Can you clarify the scope and timeline?",
    "Got it. Could you share a bit more detail so I can respond properly?",
]

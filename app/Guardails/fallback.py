def instagram_fallback(reason: str) -> str:
    if reason == "escalate":
        return "Thanks for sharing the details. I’m reviewing this internally and will get back to you shortly."
    elif reason == "block":
        return "I'm sorry, but I can't process this request. Please try again later."
    elif reason == "ok":
        return "Thank you for your message. I'll get back to you shortly."

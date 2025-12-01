import re


def extract_platform(message: str):
    """Return normalized platform if explicitly mentioned, otherwise None."""
    message_lower = message.lower()
    if "instagram" in message_lower or "insta" in message_lower:
        return "instagram"
    if "tiktok" in message_lower or "tik tok" in message_lower:
        return "tiktok"
    if "youtube" in message_lower or "yt" in message_lower:
        return "youtube"
    return None


def extract_limit(message: str):
    numbers = re.findall(r"\d+", message)
    if numbers:
        try:
            limit = int(numbers[0])
            return min(limit, 20)
        except ValueError:
            return None
    return None


def extract_country(message: str):
    """Detect country from a small controlled list, otherwise None."""
    msg = message.lower()
    countries = [
        "uae",
        "kuwait",
        "iran",
        "jordan",
        "qatar",
        "saudi arabia",
    ]
    for c in countries:
        if c in msg:
            return c
    return None


def extract_budget(message: str):
    message_lower = message.lower()
    if "budget" in message_lower:
        return "budget"
    return None

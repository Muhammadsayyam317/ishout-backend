import re


def extract_all_fields(message: str):
    """
    Extract platform, category, country, and number_of_influencers
    from the user's message.
    Returns a dict with None for missing fields.
    """

    msg = message.lower()

    # Detect platform
    platforms = ["instagram", "insta", "tiktok", "youtube", "yt"]
    platform = next((p for p in platforms if p in msg), None)
    categories = [
        "fashion",
        "beauty",
        "tech",
        "gaming",
        "fitness",
        "travel",
        "food",
        "lifestyle",
        "finance",
        "sports",
        "education",
    ]
    category = next((c for c in categories if c in msg), None)
    countries = [
        "uae",
        "kuwait",
        "iran",
        "jordan",
        "qatar",
        "saudi arabia",
    ]
    country = next((c for c in countries if c in msg), None)

    number_match = re.search(r"(\d+)\s*(influencers?|creators?)?", msg)
    number_of_influencers = int(number_match.group(1)) if number_match else None

    return {
        "platform": platform,
        "category": category,
        "country": country,
        "number_of_influencers": number_of_influencers,
    }

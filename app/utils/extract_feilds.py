import re
from typing import Optional

PLATFORM_SYNS = {
    "instagram": ["instagram", "insta", "instagtam", "instgram"],
    "tiktok": ["tiktok", "tik tok", "tik-tok"],
    "youtube": ["youtube", "yt", "you tube"],
}

CATEGORIES = [
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

COUNTRIES = [
    "uae",
    "kuwait",
    "iran",
    "jordan",
    "qatar",
    "saudi arabia",
    "saudi",
    "bahrain",
    "oman",
]


def _fuzzy_platform(msg: str) -> Optional[str]:
    for plat, synonyms in PLATFORM_SYNS.items():
        for s in synonyms:
            if s in msg:
                return plat
    return None


def extract_platform(message: str) -> Optional[str]:
    msg = (message or "").lower()
    return _fuzzy_platform(msg)


def extract_limit(message: str) -> Optional[int]:
    msg = (message or "").lower()
    m = re.search(r"(\d+)\s*(?:-|to)?\s*(\d+)?\s*(influencers?|creators?)?", msg)
    if m:
        try:
            return int(m.group(1))
        except:
            return None
    return None


def extract_country(message: str) -> Optional[str]:
    msg = (message or "").lower()
    # match exact country keywords from list
    for c in COUNTRIES:
        if c in msg:
            return c
    # try simple capitalized words (fallback) — but keep conservative
    m = re.search(r"\bin\s+([A-Za-z ]{2,30})\b", msg)
    if m:
        cand = m.group(1).strip().lower()
        if len(cand) <= 30:
            return cand
    return None


def extract_budget(message: str) -> Optional[str]:
    msg = (message or "").lower()
    m = re.search(r"\$\s?(\d{2,10})", msg)
    if m:
        return m.group(1)
    m2 = re.search(r"(\d{3,})\s*(usd|dollars)", msg)
    if m2:
        return m2.group(1)
    return None


def extract_category(message: str) -> Optional[str]:
    msg = (message or "").lower()
    for c in CATEGORIES:
        if c in msg:
            return c
    return None


def extract_all_fields(message: str):
    return {
        "platform": extract_platform(message),
        "category": extract_category(message),
        "country": extract_country(message),
        "number_of_influencers": extract_limit(message),
        "budget": extract_budget(message),
    }

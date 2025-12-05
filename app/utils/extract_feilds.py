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
    m = re.search(r"number\s+of\s+influencers?\s*(?:is|:|=)\s*(\d+)", msg)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass

    m = re.search(r"(\d+)\s+(?:number\s+of\s+)?(?:influencers?|creators?)", msg)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass

    m = re.search(r"(\d+)\s*(?:-|to)\s*(\d+)\s*(?:influencers?|creators?)?", msg)
    if m:
        try:
            return int(m.group(2) or m.group(1))
        except ValueError:
            pass
    m = re.search(r"^\s*(\d+)\s*$", msg)
    if m:
        try:
            num = int(m.group(1))
            if 1 <= num <= 100:
                return num
        except ValueError:
            pass
    m = re.search(r"(\d+)\s*(?:influencers?|creators?)", msg)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass

    return None


def extract_country(message: str) -> Optional[str]:
    msg = (message or "").lower()
    country_patterns = [
        r"country\s*(?:is|:|=)\s*([a-z\s]+?)(?:\s|$|,|category)",
        r"country\s+([a-z\s]+?)(?:\s|$|,|category)",
    ]

    for pattern in country_patterns:
        m = re.search(pattern, msg)
        if m:
            cand = m.group(1).strip().lower()
            for c in COUNTRIES:
                if c in cand or cand in c:
                    return c
            if 2 <= len(cand) <= 30:
                return cand
    for c in COUNTRIES:
        if c in msg:
            return c

    m = re.search(r"\bin\s+([A-Za-z ]{2,30})\b", msg)
    if m:
        cand = m.group(1).strip().lower()
        if len(cand) <= 30:
            return cand
    return None


# def extract_budget(message: str) -> Optional[str]:
#     msg = (message or "").lower()
#     m = re.search(r"\$\s?(\d{2,10})", msg)
#     if m:
#         return m.group(1)
#     m2 = re.search(r"(\d{3,})\s*(usd|dollars)", msg)
#     if m2:
#         return m2.group(1)
#     return None


def extract_category(message: str) -> Optional[str]:
    msg = (message or "").lower()
    category_patterns = [
        r"category\s*(?:is|:|=)\s*([a-z\s]+?)(?:\s|$|,|country|number)",
        r"category\s+([a-z\s]+?)(?:\s|$|,|country|number)",
    ]

    for pattern in category_patterns:
        m = re.search(pattern, msg)
        if m:
            cand = m.group(1).strip().lower()
            for c in CATEGORIES:
                if c in cand or cand in c:
                    return c
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
    }

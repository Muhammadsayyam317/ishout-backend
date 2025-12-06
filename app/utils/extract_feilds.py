import re
from typing import List, Optional

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
    "bahrain",
    "oman",
]

COUNTRY_MAP = {
    "saudi": "saudi arabia",
    "saudi arabia": "saudi arabia",
}


def _word_search(term: str, msg: str) -> bool:
    """Return True if term appears as a separate token in msg."""
    return re.search(rf"\b{re.escape(term)}\b", msg) is not None


def _fuzzy_platform(msg: str) -> Optional[str]:
    for plat, synonyms in PLATFORM_SYNS.items():
        for s in synonyms:
            if _word_search(s, msg):
                return plat
    return None


def extract_platform(message: str) -> Optional[str]:
    msg = (message or "").lower()
    return _fuzzy_platform(msg)


def extract_limit(message: str) -> Optional[int]:
    msg = (message or "").lower().strip()
    m = re.search(r"between\s+(\d+)\s+and\s+(\d+)", msg)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass

    patterns = [
        r"number\s+of\s+influencers?\s*(?:is|:|=)\s*(\d+)",
        r"(\d+)\s+number\s+of\s+influencers?",
        r"(\d+)\s+(?:influencers?|creators?)",
        r"(\d+)\s*(?:-|to)\s*(\d+)\s*(?:influencers?|creators?)?",
        r"^\s*(\d+)\s*$",
    ]

    for p in patterns:
        m = re.search(p, msg)
        if not m:
            continue
        try:
            if len(m.groups()) >= 2 and m.group(2):
                return int(m.group(2))
            return int(m.group(1))
        except Exception:
            pass
    if len(msg.split()) <= 3:
        m = re.search(r"\b(\d+)\b", msg)
        if m:
            try:
                return int(m.group(1))
            except Exception:
                pass

    return None


def extract_country(message: str) -> Optional[str]:
    msg = (message or "").lower()

    patterns = [
        r"country\s*(?:is|:|=)\s*([a-z\s]{2,30})",
        r"country\s+([a-z\s]{2,30})",
    ]
    for pattern in patterns:
        m = re.search(pattern, msg)
        if m:
            cand = m.group(1).strip().lower()
            for c in COUNTRIES:
                if c in cand or cand in c:
                    return COUNTRY_MAP.get(c, c)
            if 2 <= len(cand) <= 30:
                return cand
    for c in COUNTRIES:
        if _word_search(c, msg):
            return COUNTRY_MAP.get(c, c)

    m = re.search(r"\bin\s+([A-Za-z ]{2,30})\b", msg)
    if m:
        cand = m.group(1).strip().lower()
        for c in COUNTRIES:
            if c in cand or cand in c:
                return COUNTRY_MAP.get(c, c)

    return None


def extract_category(message: str) -> Optional[str]:
    msg = (message or "").lower()
    patterns = [
        r"category\s*(?:is|:|=)\s*([a-z\s]{2,30})",
        r"category\s+([a-z\s]{2,30})",
    ]
    for pattern in patterns:
        m = re.search(pattern, msg)
        if m:
            cand = m.group(1).strip().lower()
            for c in CATEGORIES:
                if c in cand or cand in c:
                    return c
            return cand

    for c in CATEGORIES:
        if _word_search(c, msg):
            return c
    return None


def _parse_follower_value(value: str) -> Optional[int]:
    value = value.strip().lower().replace(",", "")
    value = re.sub(r"[^\dkm]+$", "", value)

    if value.endswith("m"):
        try:
            num = float(value[:-1])
            return int(num * 1_000_000)
        except ValueError:
            return None
    elif value.endswith("k"):
        try:
            num = float(value[:-1])
            return int(num * 1_000)
        except ValueError:
            return None
    else:
        try:
            return int(float(value))
        except ValueError:
            return None


def extract_followers(message: str) -> Optional[List[str]]:
    msg = (message or "").lower()

    range_pattern = r"(\d+(?:\.\d+)?[km])\s*[-–—]\s*(\d+(?:\.\d+)?[km])"
    m = re.search(range_pattern, msg)
    if m:
        val1 = m.group(1)
        val2 = m.group(2)
        parsed1 = _parse_follower_value(val1)
        parsed2 = _parse_follower_value(val2)

        if parsed1 is not None and parsed2 is not None and parsed1 < parsed2:
            return [val1, val2]
    patterns = [
        r"followers?\s*(?:is|:|=)\s*(\d+(?:\.\d+)?[km]?)",
        r"followers?\s+(\d+(?:\.\d+)?[km]?)",
        r"(\d+(?:\.\d+)?[km]?)\s+followers?",
    ]
    for pattern in patterns:
        m = re.search(pattern, msg)
        if m:
            val = m.group(1)
            parsed = _parse_follower_value(val)
            if parsed is not None and parsed >= 100:
                return [val]
    standalone_pattern = r"\b(\d+(?:\.\d+)?[km])\b"
    matches = re.findall(standalone_pattern, msg)
    if matches:
        valid_matches = []
        for match in matches:
            parsed = _parse_follower_value(match)
            if parsed is not None and parsed >= 1000:
                valid_matches.append(match)
        if valid_matches:
            return valid_matches[:1] if len(valid_matches) == 1 else valid_matches[:2]

    return None


def extract_all_fields(message: str):
    return {
        "platform": extract_platform(message),
        "category": extract_category(message),
        "country": extract_country(message),
        "limit": extract_limit(message),
        "followers": extract_followers(message),
    }

from typing import Any, Dict, List, Optional, Tuple
import re
from bson import ObjectId


def parse_follower_count(value: str) -> int:
    try:
        if isinstance(value, (int, float)):
            return int(value)
        value = value.replace(",", "").replace(" ", "").upper()
        if value.endswith("K"):
            return int(float(value[:-1]) * 1000)
        elif value.endswith("M"):
            return int(float(value[:-1]) * 1000000)
        else:
            return int(float(value))
    except (ValueError, TypeError):
        print(f"Could not parse follower count: {value}")
        return 0


def parse_follower_range(value: str) -> Tuple[int, int, str]:
    try:
        if "-" not in str(value):
            count = parse_follower_count(value)
            return count, count, str(value)
        start_str, end_str = value.split("-", 1)
        start_count = parse_follower_count(start_str)
        end_count = parse_follower_count(end_str)

        return start_count, end_count, value
    except Exception as e:
        print(f"Error parsing follower range '{value}': {str(e)}")
        return 0, 0, str(value)


def parse_followers_list(followers: List[str]) -> List[Tuple[int, int]]:
    ranges = []

    for follower_str in followers:
        if not follower_str:
            continue
        if "," in follower_str:
            parts = [p.strip() for p in follower_str.split(",")]
            for part in parts:
                min_count, max_count, _ = parse_follower_range(part)
                if min_count > 0 or max_count > 0:
                    ranges.append((min_count, max_count))
        elif "-" in follower_str:
            start_str, end_str = follower_str.split("-", 1)
            start_str = start_str.strip()
            end_str = end_str.strip()
            start_upper = start_str.upper()
            if start_upper.endswith("K") and not (
                end_str.upper().endswith("K") or end_str.upper().endswith("M")
            ):
                end_str = end_str + "K"
            elif start_upper.endswith("M") and not (
                end_str.upper().endswith("K") or end_str.upper().endswith("M")
            ):
                end_str = end_str + "M"

            min_count, max_count, _ = parse_follower_range(f"{start_str}-{end_str}")
            if min_count > 0 or max_count > 0:
                ranges.append((min_count, max_count))
        else:
            min_count, max_count, _ = parse_follower_range(follower_str)
            if min_count > 0 or max_count > 0:
                ranges.append((min_count, max_count))

    return ranges


def format_followers_for_query(followers: List[str]) -> str:
    if not followers:
        return ""

    ranges = parse_followers_list(followers)
    if not ranges:
        return ""

    descriptions = []
    for min_count, max_count in ranges:
        if min_count == max_count:
            if min_count >= 1000000:
                descriptions.append(f"{min_count/1000000:.1f}M")
            elif min_count >= 1000:
                descriptions.append(f"{min_count/1000:.0f}K")
            else:
                descriptions.append(str(min_count))
        else:
            min_str = (
                f"{min_count/1000000:.1f}M"
                if min_count >= 1000000
                else f"{min_count/1000:.0f}K" if min_count >= 1000 else str(min_count)
            )
            max_str = (
                f"{max_count/1000000:.1f}M"
                if max_count >= 1000000
                else f"{max_count/1000:.0f}K" if max_count >= 1000 else str(max_count)
            )
            descriptions.append(f"{min_str}-{max_str}")

    return ", ".join(descriptions)


def matches_follower_count(
    follower_count: Any, follower_ranges: List[Tuple[int, int]]
) -> bool:
    if not follower_ranges:
        return True
    if follower_count is None:
        return False
    try:
        if isinstance(follower_count, str):
            count = parse_follower_count(follower_count)
        elif isinstance(follower_count, (int, float)):
            count = int(follower_count)
        else:
            return False
        for min_count, max_count in follower_ranges:
            if min_count <= count <= max_count:
                return True

        return False
    except Exception:
        return False


def build_combination_query(
    platform: str,
    category: Optional[str],
    country: Optional[str],
    follower_range_str: Optional[str],
) -> str:
    query_parts = []
    if category:
        query_parts.append(f"category: {category}")
    if country:
        query_parts.append(f"country: {country}")
    if follower_range_str:
        follower_str = format_followers_for_query([follower_range_str])
        if follower_str:
            query_parts.append(f"follower counts: {follower_str}")

    query = f"Find {platform} influencers"
    if query_parts:
        query += " matching " + ", ".join(query_parts)
    query += "."

    return query


def extract_influencer_data(result, platform: str) -> Dict[str, Any]:
    return {
        "username": result.metadata.get("influencer_username"),
        "followers": result.metadata.get("followers"),
        "country": result.metadata.get("country"),
        "bio": result.metadata.get("bio"),
        "engagementRate": result.metadata.get("engagementRate"),
        "picture": result.metadata.get("pic"),
        "platform": platform.lower(),
        "id": result.metadata.get("id"),
    }


def matches_country_filter(
    influencer_country: Optional[str], filter_country: Optional[str]
) -> bool:
    if not filter_country:
        return True
    if not influencer_country:
        return False
    filter_lower = filter_country.lower()
    influencer_lower = influencer_country.lower()

    return filter_lower in influencer_lower or influencer_lower in filter_lower


def filter_influencer_data(
    influencer_data: Dict[str, Any],
    combination_follower_ranges: List[Tuple[int, int]],
    all_follower_ranges: List[Tuple[int, int]],
    filter_country: Optional[str],
) -> bool:

    if combination_follower_ranges:
        if not matches_follower_count(
            influencer_data["followers"], combination_follower_ranges
        ):
            return False
    elif all_follower_ranges:
        if not matches_follower_count(
            influencer_data["followers"], all_follower_ranges
        ):
            return False
    if not matches_country_filter(influencer_data.get("country"), filter_country):
        return False

    return True


def convert_objectid(doc):
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
    return doc


def convert_to_number(v: str):
    v = v.lower().replace(" ", "")
    if "k" in v:
        return int(float(v.replace("k", "")) * 1000)
    if "m" in v:
        return int(float(v.replace("m", "")) * 1_000_000)
    return int(v)


def normalize_followers(followers: list[str]) -> list[str]:
    ranges = []
    for f in followers:
        if "-" in f:
            ranges.append(f)
        else:
            num = int(f.replace("k", "000").replace("K", "000"))
            if num <= 50000:
                ranges.append("0-50k")
            elif num <= 100000:
                ranges.append("50k-100k")
            elif num <= 200000:
                ranges.append("100k-200k")
            else:
                ranges.append(f"{num//1000}k-{num//1000*2}k")
    return ranges


def normalize_country(country: str) -> str:
    mapping = {
        "egypt": "Egypt",
        "iraq": "Iraq",
        "lebanon": "Lebanon",
        "jordan": "Jordan",
        "kuwait": "Kuwait",
        "oman": "Oman",
        "qatar": "Qatar",
        "saudi": "Saudi Arabia",
        "uae": "United Arab Emirates",
    }
    return mapping.get(country.lower(), country)


def followers_in_range(influencer_count: int, ranges: List[Tuple[int, int]]):
    if not ranges:
        return True
    for min_f, max_f in ranges:
        if min_f <= influencer_count <= max_f:
            return True
    return False


def normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    return re.sub(r"[^\d]", "", phone)


def format_followers(count):
    if isinstance(count, (int, float)):
        if count >= 1_000_000:
            return f"{count/1_000_000:.1f}M"
        if count >= 1_000:
            return f"{count/1_000:.1f}K"
        return str(count)
    return "N/A"

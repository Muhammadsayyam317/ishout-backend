from typing import List, Tuple
import math


def plan_limits(user_limit: int, categories: List[str], followers_list: List[str], countries: List[str]) -> Tuple[int, int]:
    """Compute adjusted global limit and per-combination limit.

    - Doubles the requested limit (agentic generosity)
    - Distributes across combinations to prevent explosion

    Returns:
        (adjusted_global_limit, per_call_limit)
    """
    try:
        requested = int(user_limit)
    except Exception:
        requested = 5

    adjusted_global_limit = max(1, requested * 2)

    safe_categories = categories or []
    safe_followers_list = followers_list or [""]
    safe_countries = countries or [None]

    combinations_count = max(1, len(safe_categories) * len(safe_followers_list) * len(safe_countries))
    per_call_limit = max(1, math.ceil(adjusted_global_limit / combinations_count))

    return adjusted_global_limit, per_call_limit



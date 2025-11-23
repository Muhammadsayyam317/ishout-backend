# from typing import List, Dict, Any, Optional


# def _norm_score(v: Optional[float]) -> float:
#     try:
#         if v is None:
#             return 0.0
#         return float(v)
#     except Exception:
#         return 0.0


# def sort_and_diversify(influencers: List[Dict[str, Any]], *, diversify_by: str = "platform") -> List[Dict[str, Any]]:
#     """Sort by similarity_score desc (if present), then diversify across a key to avoid clumping.

#     Simple greedy round-robin by group after sorting. Keeps stable ordering inside each group.
#     """
#     # primary sort by similarity_score desc if available
#     sorted_items = sorted(
#         influencers,
#         key=lambda x: _norm_score(x.get("similarity_score")),
#         reverse=True,
#     )

#     # bucket by diversify key
#     groups: Dict[str, List[Dict[str, Any]]] = {}
#     for item in sorted_items:
#         key = str(item.get(diversify_by, ""))
#         groups.setdefault(key, []).append(item)

#     # round-robin pick
#     diversified: List[Dict[str, Any]] = []
#     while True:
#         progressed = False
#         for key in list(groups.keys()):
#             bucket = groups[key]
#             if bucket:
#                 diversified.append(bucket.pop(0))
#                 progressed = True
#         if not progressed:
#             break

#     return diversified

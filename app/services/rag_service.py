from typing import Dict, Any, List, Optional, Callable
from app.services.embedding_service import query_vector_store


def _build_dedupe_key(doc: Dict[str, Any]) -> Optional[str]:
    if not isinstance(doc, dict):
        return None
    return (
        doc.get("_id")
        or doc.get("id")
        or doc.get("username")
        or doc.get("handle")
        or doc.get("url")
        or doc.get("profile_url")
    )


async def retrieve_with_rag_then_fallback(
    *,
    platform: str,
    category: str,
    country: Optional[str],
    raw_followers: str,
    min_followers: Optional[int],
    max_followers: Optional[int],
    per_call_limit: int,
    tool_call: Callable[..., Any],
    query: str,
    seen_keys: set,
    exclude_keys: Optional[set] = None,
) -> List[Dict[str, Any]]:
    """RAG-first retrieval with fallback to platform tool and enrichment.

    Returns a list of enriched influencer dicts.
    """
    influencers: List[Dict[str, Any]] = []

    rag_docs = await query_vector_store(
        query=query,
        platform=platform,
        limit=per_call_limit,
        min_followers=min_followers,
        max_followers=max_followers,
        country=country,
    )

    for doc in rag_docs:
        key = _build_dedupe_key(doc)
        if key and key not in seen_keys and (not exclude_keys or key not in exclude_keys):
            seen_keys.add(key)
            enriched = dict(doc)
            enriched.setdefault("platform", platform)
            enriched.setdefault("category", category)
            if country:
                enriched.setdefault("country", country)
            influencers.append(enriched)

    if len(influencers) < per_call_limit:
        need = per_call_limit - len(influencers)
        api_result = await tool_call(
            query=query,
            limit=need,
            min_followers=min_followers,
            max_followers=max_followers,
            country=country,
        )
        api_influencers = api_result.get("influencers", [])
        for inf in api_influencers:
            key = _build_dedupe_key(inf)
            if key and key not in seen_keys and (not exclude_keys or key not in exclude_keys):
                seen_keys.add(key)
                enriched = dict(inf)
                enriched.setdefault("platform", platform)
                enriched.setdefault("category", category)
                if country:
                    enriched.setdefault("country", country)
                influencers.append(enriched)

    return influencers



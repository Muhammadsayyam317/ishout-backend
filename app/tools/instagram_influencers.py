from typing import List, Optional, Set
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai.embeddings import OpenAIEmbeddings
from app.config.credentials_config import config
from app.db.connection import get_pymongo_db
from app.utils.helpers import (
    extract_influencer_data,
    filter_influencer_data,
    normalize_country,
    normalize_followers,
    parse_followers_list,
)


async def search_instagram_influencers(
    category: List[str],
    limit: int,
    followers: List[str],
    country: List[str],
    exclude_ids: Optional[List[str]] = None,
):
    try:
        excluded_ids = set(exclude_ids or [])
        categories = category if category else [""]
        countries = [normalize_country(c) for c in country] if country else [""]
        followers_list = normalize_followers(followers) if followers else [""]
        all_follower_ranges = parse_followers_list(followers_list)
        embeddings = OpenAIEmbeddings(
            api_key=config.OPENAI_API_KEY,
            model=config.EMBEDDING_MODEL,
        )
        pymongo_db = get_pymongo_db()
        collection = pymongo_db[config.MONGODB_ATLAS_COLLECTION_INSTAGRAM]
        vectorstore = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name="vector_index",
            embedding_key="embedding",
            text_key="pageContent",
            relevance_score_fn="cosine",
        )

        seen_usernames: Set[str] = set()
        all_results = []
        target_limit = limit * 2
        per_combination_limit = max(50, target_limit * 2)

        for cat in categories:
            for cntry in countries:
                for follower_range_str in followers_list:
                    query_text = f"Instagram influencer {cat} from {cntry} with {follower_range_str} followers"
                    results = vectorstore.similarity_search(
                        query_text, k=per_combination_limit
                    )

                    for r in results:
                        influencer_data = extract_influencer_data(r, "Instagram")
                        username = influencer_data.get("username")

                        if not username or username in seen_usernames:
                            continue
                        if influencer_data.get("id") in excluded_ids:
                            continue
                        if not filter_influencer_data(
                            influencer_data,
                            parse_followers_list([follower_range_str]),
                            all_follower_ranges,
                            cntry,
                        ):
                            continue

                        seen_usernames.add(username)
                        all_results.append(influencer_data)

                        if len(all_results) >= target_limit:
                            break
                    if len(all_results) >= target_limit:
                        break
                if len(all_results) >= target_limit:
                    break
            if len(all_results) >= target_limit:
                break
        if not all_results:
            return {
                "data": [],
                "message": "No influencers found for the selected filters.",
            }

        return {
            "data": all_results[:target_limit],
            "message": f"Found {len(all_results[:target_limit])} influencers.",
        }

    except Exception as e:
        raise ValueError(f"Error searching Instagram influencers: {str(e)}") from e

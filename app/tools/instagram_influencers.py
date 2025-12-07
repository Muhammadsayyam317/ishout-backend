from typing import List, Set
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai.embeddings import OpenAIEmbeddings
from app.config.credentials_config import config
from app.db.connection import get_pymongo_db
from app.utils.helpers import (
    extract_influencer_data,
    followers_in_range,
    normalize_follower_value,
)


async def search_instagram_influencers(
    category: List[str], limit: int, followers: List[str], country: List[str]
):
    try:
        print(
            f"INSTAGRAM TOOL CALLED WITH: category={category}, followers={followers}, country={country}, limit={limit}"
        )

        categories = [c.strip().title() for c in category if c.strip()] or [""]
        countries = [c.strip().title() for c in country if c.strip()] or [""]
        followers_list = [f.strip() for f in followers if f.strip()] or [""]

        normalized_ranges = []
        for f in followers_list:
            normalized_ranges.append(normalize_follower_value(f))

        embeddings = OpenAIEmbeddings(
            api_key=config.OPENAI_API_KEY, model=config.EMBEDDING_MODEL
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
        target_limit = limit * 2 if limit > 0 else None
        per_combination_limit = max(50, target_limit) if target_limit else 50

        for cat in categories:
            for cntry in countries:
                for fr in followers_list:
                    query_text = (
                        f"Instagram influencer {cat} from {cntry} with {fr} followers"
                    )
                    print(f"INSTAGRAM VECTOR QUERY: {query_text}")

                    results = vectorstore.similarity_search(
                        query_text, k=per_combination_limit
                    )

                    for r in results:
                        influencer_data = extract_influencer_data(r, "Instagram")
                        username = influencer_data.get("username")

                        followers_count = influencer_data.get("followers", 0)
                        if normalized_ranges and not followers_in_range(
                            followers_count, normalized_ranges
                        ):
                            continue

                        if username and username in seen_usernames:
                            continue

                        seen_usernames.add(username)
                        all_results.append(influencer_data)

                        if target_limit and len(all_results) >= target_limit:
                            break

        return all_results[:target_limit] if target_limit else all_results

    except Exception as e:
        raise ValueError(f"Error searching Instagram influencers: {str(e)}")

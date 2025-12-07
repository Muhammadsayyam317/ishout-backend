from typing import List, Set
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai.embeddings import OpenAIEmbeddings
from app.config.credentials_config import config
from app.db.connection import get_pymongo_db
from app.utils.helpers import (
    build_combination_query,
    extract_influencer_data,
    filter_influencer_data,
    parse_followers_list,
)


async def search_instagram_influencers(
    category: List[str], limit: int, followers: List[str], country: List[str]
):
    try:
        print(
            f"INSTAGRAM TOOL CALLED WITH: category: {category}, followers: {followers}, country: {country}, limit: {limit}"
        )
        categories = category if category else [""]
        countries = country if country else [""]
        followers_list = followers if followers else [""]
        all_follower_ranges = (
            parse_followers_list(followers_list) if followers_list else []
        )
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
                for follower_range_str in followers_list:
                    query_text = f"Instagram influencer {cat} from {cntry} with {follower_range_str} followers"
                    print(f"INSTAGRAM VECTOR QUERY: {query_text}")
                    results = vectorstore.similarity_search(
                        query_text, k=per_combination_limit
                    )
                    for r in results:
                        influencer_data = extract_influencer_data(r, "Instagram")
                        username = influencer_data.get("username")
                        if username and username in seen_usernames:
                            continue

                        if username:
                            seen_usernames.add(username)
                        all_results.append(influencer_data)
                        # Stop collecting if we've reached the target limit
                        if target_limit and len(all_results) >= target_limit:
                            break
                    if target_limit and len(all_results) >= target_limit:
                        break
                if target_limit and len(all_results) >= target_limit:
                    break
            if target_limit and len(all_results) >= target_limit:
                break

        # Return limited results
        return all_results[:target_limit] if target_limit else all_results
    except Exception as e:
        raise ValueError(f"Error searching Instagram influencers: {str(e)}")

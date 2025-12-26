from typing import Set
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from app.config.credentials_config import config
from app.db.connection import get_pymongo_db
from app.utils.helpers import (
    extract_influencer_data,
    filter_influencer_data,
    normalize_country,
    normalize_followers,
    parse_followers_list,
)


async def vector_search_influencers(
    *,
    platform_name: str,
    mongo_collection: str,
    category,
    followers,
    country,
    limit,
    generated_ids=None,
    rejected_ids=None,
):
    excluded_ids = set(generated_ids or []) | set(rejected_ids or [])

    categories = category or [""]
    countries = [normalize_country(c) for c in country] if country else [""]
    followers_list = normalize_followers(followers) if followers else [""]

    follower_ranges = parse_followers_list(followers_list)

    embeddings = OpenAIEmbeddings(
        api_key=config.OPENAI_API_KEY,
        model=config.EMBEDDING_MODEL,
    )

    db = get_pymongo_db()
    collection = db[mongo_collection]

    vectorstore = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name="vector_index",
        embedding_key="embedding",
        text_key="pageContent",
        relevance_score_fn="cosine",
    )

    seen_usernames: Set[str] = set()
    results = []

    target_limit = limit * 2
    per_query_limit = max(50, target_limit * 2)

    for cat in categories:
        for cntry in countries:
            for follower_range in followers_list:
                query = (
                    f"{platform_name} influencer {cat} "
                    f"from {cntry} with {follower_range} followers"
                )

                docs = vectorstore.similarity_search(query, k=per_query_limit)

                for doc in docs:
                    influencer = extract_influencer_data(doc, platform_name)

                    influencer_id = influencer.get("id")
                    username = influencer.get("username")

                    if not influencer_id or influencer_id in excluded_ids:
                        continue
                    if username in seen_usernames:
                        continue

                    if not filter_influencer_data(
                        influencer,
                        parse_followers_list([follower_range]),
                        follower_ranges,
                        cntry,
                    ):
                        continue

                    seen_usernames.add(username)
                    results.append(influencer)

                    if len(results) >= target_limit:
                        break

                if len(results) >= target_limit:
                    break

    return {
        "data": results[:limit],
        "message": "Success" if results else "No influencers found",
    }

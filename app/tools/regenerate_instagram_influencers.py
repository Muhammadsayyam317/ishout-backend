# app/tools/regenerate_instagram_influencers.py

from typing import Set
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai.embeddings import OpenAIEmbeddings

from app.config.credentials_config import config
from app.db.connection import get_pymongo_db
from app.models.reject_influencer_model import (
    SearchRejectRegenerateInfluencersRequest,
)
from app.utils.helpers import (
    extract_influencer_data,
    filter_influencer_data,
    normalize_country,
    normalize_followers,
    parse_followers_list,
)


async def regenerate_instagram_influencer(
    request_data: SearchRejectRegenerateInfluencersRequest,
):
    excluded_ids = set(request_data.generated_influencers_id or []) | set(
        request_data.rejected_influencers_id or []
    )
    categories = request_data.category or [""]
    countries = [normalize_country(c) for c in request_data.country] or [""]
    followers_list = normalize_followers(request_data.followers) or [""]
    follower_ranges = parse_followers_list(followers_list)

    embeddings = OpenAIEmbeddings(
        api_key=config.OPENAI_API_KEY,
        model=config.EMBEDDING_MODEL,
    )

    db = get_pymongo_db()
    collection = db[config.MONGODB_ATLAS_COLLECTION_INSTAGRAM]

    vectorstore = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name="vector_index",
        embedding_key="embedding",
        text_key="pageContent",
        relevance_score_fn="cosine",
    )

    seen_usernames: Set[str] = set()
    for cat in categories:
        for cntry in countries:
            for follower_range in followers_list:
                query = (
                    f"Instagram influencer {cat} from {cntry} "
                    f"with {follower_range} followers"
                )
                docs = vectorstore.similarity_search(query, k=50)
                for doc in docs:
                    influencer = extract_influencer_data(doc, "Instagram")
                    influencer_id = influencer.get("id")
                    username = influencer.get("username")
                    if not influencer_id or not username:
                        continue
                    if influencer_id in excluded_ids:
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

                    return influencer

    return None

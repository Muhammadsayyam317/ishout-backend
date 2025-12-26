from typing import Set
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai.embeddings import OpenAIEmbeddings

from app.config.credentials_config import config
from app.db.connection import get_pymongo_db
from app.Schemas.reject_influencer import (
    SearchRejectRegenerateInfluencersRequest,
)
from app.utils.helpers import (
    extract_influencer_data,
    filter_influencer_data,
    normalize_country,
    normalize_followers,
    parse_followers_list,
)


async def regenerate_youtube_influencer(
    request_data: SearchRejectRegenerateInfluencersRequest,
):
    excluded_ids: Set[str] = set(request_data.generated_influencers_id or []) | set(
        request_data.rejected_influencers_id or []
    )

    categories = request_data.category or [""]
    countries = (
        [normalize_country(c) for c in request_data.country]
        if request_data.country
        else [""]
    )
    followers_list = (
        normalize_followers(request_data.followers) if request_data.followers else [""]
    )

    all_follower_ranges = parse_followers_list(followers_list)
    embeddings = OpenAIEmbeddings(
        api_key=config.OPENAI_API_KEY,
        model=config.EMBEDDING_MODEL,
    )

    db = get_pymongo_db()
    collection = db[config.MONGODB_ATLAS_COLLECTION_YOUTUBE]
    vectorstore = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name="vector_index",
        embedding_key="embedding",
        text_key="text",
        relevance_score_fn="cosine",
    )

    seen_usernames: Set[str] = set()

    for cat in categories:
        for cntry in countries:
            for follower_range_str in followers_list:

                query_text = (
                    f"YouTube influencer {cat} from {cntry} "
                    f"with {follower_range_str} followers"
                )
                results = vectorstore.similarity_search(query_text, k=50)
                for r in results:
                    influencer_data = extract_influencer_data(r, "YouTube")
                    influencer_id = influencer_data.get("id")
                    username = influencer_data.get("username")

                    if not influencer_id or not username:
                        continue
                    if influencer_id in excluded_ids:
                        continue
                    if username in seen_usernames:
                        continue
                    if not filter_influencer_data(
                        influencer_data,
                        parse_followers_list([follower_range_str]),
                        all_follower_ranges,
                        cntry,
                    ):
                        continue

                    seen_usernames.add(username)
                    return influencer_data
    return None

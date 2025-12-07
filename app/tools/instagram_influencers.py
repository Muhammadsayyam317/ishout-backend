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
            f"\nINSTAGRAM TOOL CALLED:\n"
            f"Category={category} | Country={country} | Followers={followers} | Limit={limit}"
        )

        # Normalize inputs
        categories = [c.strip() for c in category if c.strip()]
        countries = [c.strip() for c in country if c.strip()]
        follower_inputs = [f.strip() for f in followers if f.strip()]

        normalized_ranges = (
            [normalize_follower_value(f) for f in follower_inputs]
            if follower_inputs
            else []
        )

        # Setup vector store
        embeddings = OpenAIEmbeddings(
            api_key=config.OPENAI_API_KEY, model=config.EMBEDDING_MODEL
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

        # =====================
        # BUILD SEARCH QUERY
        # =====================

        cat_str = ", ".join(categories) if categories else "any category"
        country_str = ", ".join(countries) if countries else "any country"
        followers_str = (
            ", ".join(follower_inputs) if follower_inputs else "any followers"
        )

        search_query = (
            f"Instagram influencer in {cat_str}, located in {country_str}, "
            f"with follower range {followers_str}"
        )

        print(f"INSTAGRAM VECTOR QUERY: {search_query}")

        # Strong search: 3x limit
        primary_k = max(50, limit * 3)
        results = vectorstore.similarity_search(search_query, k=primary_k)

        # Fallback search (if too few results)
        if len(results) < limit:
            fallback_query = f"Instagram influencer {cat_str}"
            print(f"FALLBACK SEARCH USED: {fallback_query}")
            fallback_results = vectorstore.similarity_search(
                fallback_query, k=primary_k
            )
            results.extend(fallback_results)

        # =====================
        # FILTERING
        # =====================

        final_list = []
        seen_usernames: Set[str] = set()

        for r in results:
            data = extract_influencer_data(r, "Instagram")
            username = data.get("username")
            country_val = data.get("country", "")
            followers_count = data.get("followers", 0)

            # Deduplicate
            if username in seen_usernames:
                continue

            # Filter: country
            if countries and country_val not in countries:
                continue

            # Filter: followers
            if normalized_ranges and not followers_in_range(
                followers_count, normalized_ranges
            ):
                continue

            # Filter: category keyword match
            if categories:
                if not any(cat.lower() in str(data).lower() for cat in categories):
                    continue

            seen_usernames.add(username)
            final_list.append(data)

            # STOP WHEN LIMIT REACHED
            if len(final_list) >= limit:
                break

        print(f"FINAL INFLUENCERS FOUND: {len(final_list)} / {limit}")

        return final_list

    except Exception as e:
        raise ValueError(f"Error searching Instagram influencers: {str(e)}")

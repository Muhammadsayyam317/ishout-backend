import logging
from typing import List, Optional
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from app.config import config
from app.db.connection import get_pymongo_db

logger = logging.getLogger(__name__)
print(f"[find_influencers_for_whatsapp] Logger: {logger}")


def find_influencers_for_whatsapp(
    query: str,
    platform: str,
    number_of_influencers: int,
    country: Optional[str] = None,
) -> List[dict]:
    print(f"[find_influencers_for_whatsapp] Query: {query}")
    print(f"[find_influencers_for_whatsapp] Platform: {platform}")
    print(
        f"[find_influencers_for_whatsapp] Number of influencers: {number_of_influencers}"
    )
    print(f"[find_influencers_for_whatsapp] Country: {country}")
    logger.info(
        f"[find_influencers_for_whatsapp] Called with - query: '{query}', platform: '{platform}', number_of_influencers: {number_of_influencers}, country: '{country}'"
    )
    try:
        collection_map = {
            "instagram": config.MONGODB_ATLAS_COLLECTION_INSTAGRAM,
            "tiktok": config.MONGODB_ATLAS_COLLECTION_TIKTOK,
            "youtube": config.MONGODB_ATLAS_COLLECTION_YOUTUBE,
        }
        if platform not in collection_map:
            raise ValueError(f"Invalid platform: {platform}")
        collection = get_pymongo_db()[collection_map[platform]]
        logger.info(
            f"[find_influencers_for_whatsapp] Using collection: {collection_map[platform]}"
        )
        embeddings = OpenAIEmbeddings(
            api_key=config.OPENAI_API_KEY,
            model=config.EMBEDDING_MODEL,
        )
        store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name=f"embedding_index_{platform}",
            relevance_score="cosine",
        )

        store.create_vector_search_index(dimensions=1536)
        logger.info(
            f"[find_influencers_for_whatsapp] Performing similarity search with query: '{query}', k: {number_of_influencers}"
        )
        docs = store.similarity_search(query, k=number_of_influencers)
        logger.info(f"[find_influencers_for_whatsapp] Found {len(docs)} documents")

        result = [doc.page_content for doc in docs]
        logger.info(
            f"[find_influencers_for_whatsapp] Returning {len(result)} influencers"
        )
        return result

    except Exception as e:
        logger.error(f"Error finding influencers for WhatsApp: {str(e)}", exc_info=True)
        return []

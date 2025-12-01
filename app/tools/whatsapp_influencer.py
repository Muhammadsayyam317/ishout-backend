import logging
from typing import List, Optional
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from app.config import config
from app.db.connection import get_pymongo_db

logger = logging.getLogger(__name__)


def find_influencers_for_whatsapp(
    query: str,
    platform: str,
    number_of_influencers: int,
    country: Optional[str] = None,
) -> List[dict]:
    try:
        collection_map = {
            "instagram": config.MONGODB_ATLAS_COLLECTION_INSTAGRAM,
            "tiktok": config.MONGODB_ATLAS_COLLECTION_TIKTOK,
            "youtube": config.MONGODB_ATLAS_COLLECTION_YOUTUBE,
        }
        if platform not in collection_map:
            raise ValueError(f"Invalid platform: {platform}")
        collection = get_pymongo_db()[collection_map[platform]]
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
        docs = store.similarity_search(query, k=number_of_influencers)

        return [doc.page_content for doc in docs]

    except Exception as e:
        logger.error(f"Error finding influencers for WhatsApp: {str(e)}", exc_info=True)
        return []

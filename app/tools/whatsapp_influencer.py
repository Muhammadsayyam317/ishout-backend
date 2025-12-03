import logging
from typing import List, Optional
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from app.config import config
from app.db.connection import get_pymongo_db

logger = logging.getLogger(__name__)
print(f"[find_influencers_for_whatsapp] Logger: {logger}")


def find_influencers_for_whatsapp(
    platform: str,
    category: str,
    number_of_influencers: int,
    country: Optional[str] = None,
) -> List[dict]:
    query = f"Find {number_of_influencers} {category} influencers on {platform} in {country or 'any'}".strip()
    print(f"[find_influencers_for_whatsapp] Query: {query}")
    try:
        collection_name = None
        text_key = None
        if platform.lower() == "instagram":
            collection_name = config.MONGODB_ATLAS_COLLECTION_INSTAGRAM
            text_key = "pageContent"

        elif platform.lower() == "tiktok":
            collection_name = config.MONGODB_ATLAS_COLLECTION_TIKTOK
            text_key = "pageContent"

        elif platform.lower() == "youtube":
            collection_name = config.MONGODB_ATLAS_COLLECTION_YOUTUBE
            text_key = "text"

        else:
            raise ValueError(f"Invalid platform specified: {platform}")
        if not collection_name:
            raise ValueError(
                f"Collection name is empty for platform {platform}. Check your environment variables."
            )
        collection = get_pymongo_db()[collection_name]
        print(f"[find_influencers_for_whatsapp] Using collection: {collection_name}")
        embeddings = OpenAIEmbeddings(
            api_key=config.OPENAI_API_KEY,
            model=config.EMBEDDING_MODEL,
        )
        store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name=f"embedding_index_{platform}",
            text_key=text_key,
            embedding_key="embedding",
            relevance_score_fn="cosine",
        )
        print(f"[find_influencers_for_whatsapp] Query: {query}")
        docs = store.similarity_search(query, k=number_of_influencers)
        result = [doc.page_content for doc in docs]
        return result

    except Exception as e:
        logger.error(f"Error finding influencers for WhatsApp: {str(e)}", exc_info=True)
        return []

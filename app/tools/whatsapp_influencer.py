import logging
from typing import List, Optional
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from app.db.connection import get_db
from app.config import config

logger = logging.getLogger(__name__)


async def find_influencers_for_whatsapp(
    query: str,
    platform: str,
    number_of_influencers: int,
    country: Optional[str] = None,
) -> List[dict]:
    try:
        collection_name = None
        if platform == "instagram":
            collection_name = config.MONGODB_ATLAS_COLLECTION_INSTAGRAM
        elif platform == "tiktok":
            collection_name = config.MONGODB_ATLAS_COLLECTION_TIKTOK
        elif platform == "youtube":
            collection_name = config.MONGODB_ATLAS_COLLECTION_YOUTUBE
        else:
            raise ValueError(f"Invalid platform specified: {platform}")

        if not collection_name:
            raise ValueError(
                f"Collection name is empty for platform {platform}. Check your environment variables."
            )
        embeddings = OpenAIEmbeddings(
            api_key=config.OPENAI_API_KEY, model=config.EMBEDDING_MODEL
        )
        collection = get_db().get_collection(collection_name)
        store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name=f"embedding_index_{platform}",
            relevance_score="cosine",
        ).create_vector_search_index(dimension=1536)
        result = await store.similarity_search(query, k=number_of_influencers)
        for res in result:
            result.append(res.page_content)
        return result

    except Exception as e:
        logger.error(f"Error finding influencers for WhatsApp: {str(e)}", exc_info=True)
        return []

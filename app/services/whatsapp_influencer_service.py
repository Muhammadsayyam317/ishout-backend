import asyncio
import logging
from typing import List
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from app.db.connection import get_pymongo_db
from app.config import config

logger = logging.getLogger(__name__)


async def find_influencers_for_whatsapp(
    query: str,
    platform: str,
    limit: int = 10,
) -> List[dict]:
    """
    Find influencers for WhatsApp users using vector search.
    Returns a list of influencer dictionaries with username, followers, bio, etc.
    """
    try:
        collection_name = None
        if platform == "instagram":
            collection_name = config.MONGODB_ATLAS_COLLECTION_INSTAGRAM
            text_key = "pageContent"
        elif platform == "tiktok":
            collection_name = config.MONGODB_ATLAS_COLLECTION_TIKTOK
            text_key = "pageContent"
        elif platform == "youtube":
            collection_name = config.MONGODB_ATLAS_COLLECTION_YOUTUBE
            text_key = "text"
        else:
            raise ValueError(f"Invalid platform specified: {platform}")

        if not collection_name:
            raise ValueError(
                f"Collection name is empty for platform {platform}. Check your environment variables."
            )
        embeddings = OpenAIEmbeddings(
            api_key=config.OPENAI_API_KEY, model=config.EMBEDDING_MODEL
        )
        pymongo_db = get_pymongo_db()
        collection = pymongo_db[collection_name]
        vectorstore = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name="vector_index",
            embedding_key="embedding",
            text_key=text_key,
            relevance_score_fn="cosine",
        )
        results = await asyncio.to_thread(vectorstore.similarity_search, query, k=limit)
        influencers = []
        for doc in results:
            if hasattr(doc, "metadata") and doc.metadata:
                influencer_data = {
                    "username": doc.metadata.get("influencer_username")
                    or doc.metadata.get("username"),
                    "name": doc.metadata.get("name"),
                    "followers": doc.metadata.get("followers")
                    or doc.metadata.get("follower_count"),
                    "follower_count": doc.metadata.get("follower_count")
                    or doc.metadata.get("followers"),
                    "country": doc.metadata.get("country"),
                    "bio": doc.metadata.get("bio") or doc.metadata.get("description"),
                    "description": doc.metadata.get("description")
                    or doc.metadata.get("bio"),
                    "engagementRate": doc.metadata.get("engagementRate"),
                    "picture": doc.metadata.get("pic") or doc.metadata.get("picture"),
                    "platform": platform.lower(),
                    "id": doc.metadata.get("id") or doc.metadata.get("_id"),
                }
                influencer_data = {
                    k: v for k, v in influencer_data.items() if v is not None
                }
                influencers.append(influencer_data)

        logger.info(f"Found {len(influencers)} influencers for platform {platform}")
        return influencers

    except Exception as e:
        logger.error(f"Error finding influencers for WhatsApp: {str(e)}", exc_info=True)
        return []

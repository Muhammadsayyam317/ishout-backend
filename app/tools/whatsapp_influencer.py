import logging
from typing import List, Optional
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from app.db.connection import get_db
from app.config import config
from app.utils.helpers import extract_influencer_data, matches_country_filter

logger = logging.getLogger(__name__)


async def find_influencers_for_whatsapp(
    query: str,
    platform: str,
    limit: int = 10,
    country: Optional[str] = None,
    budget: Optional[str] = None,
    influencer_limit: Optional[int] = None,
) -> List[dict]:
    """
    Find influencers for WhatsApp using vector search.

    Args:
        query: Search query text
        platform: Platform name (instagram, tiktok, youtube)
        limit: Maximum number of results to return
        country: Optional country filter (applied after search)
        budget: Optional budget filter (currently not implemented)
        influencer_limit: Optional limit override (uses limit if not provided)

    Returns:
        List of influencer dictionaries
    """
    try:
        # Determine collection name based on platform
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

        # Create embeddings and vector store
        embeddings = OpenAIEmbeddings(
            api_key=config.OPENAI_API_KEY, model=config.EMBEDDING_MODEL
        )
        collection = get_db().get_collection(collection_name)
        vectorstore = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name=f"embedding_index_{platform}",
            relevance_score="cosine",
        ).create_vector_search(dimension=1536)

        # Perform similarity search (only accepts query and k parameters)
        search_limit = (
            influencer_limit if influencer_limit else limit * 2
        )  # Get more results for filtering
        search_results = await vectorstore.similarity_search(query, k=search_limit)

        # Extract influencer data from results
        influencers = []
        for result in search_results:
            try:
                influencer_data = extract_influencer_data(result, platform.capitalize())

                # Apply country filter if provided
                if country and not matches_country_filter(
                    influencer_data.get("country"), country
                ):
                    continue

                influencers.append(influencer_data)

                # Stop if we've reached the desired limit
                if len(influencers) >= limit:
                    break

            except Exception as e:
                logger.warning(f"Error extracting influencer data: {e}")
                continue

        return influencers

    except Exception as e:
        logger.error(f"Error finding influencers for WhatsApp: {str(e)}", exc_info=True)
        return []

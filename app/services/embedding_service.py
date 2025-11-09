from typing import List, Optional, Dict, Any
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from bson import ObjectId
from app.db.connection import get_db
from app.config import config

embeddings = None


async def query_vector_store(
    query: str,
    platform: str,
    limit: int = 10,
    min_followers: Optional[int] = None,
    max_followers: Optional[int] = None,
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
        ).create_vector_search(dimension=1536)
        result = await store.similarity_search(query, k=limit)
        for res in result:
            result.append(res.page_content)
        return result
    except Exception as e:
        print(f"Error querying vector store: {str(e)}")
        return []


async def delete_from_vector_store(platform: str, influencer_id: str) -> Dict[str, Any]:
    """Delete one or more documents (and their embeddings) from the platform's collection.

    Deleting the document(s) from the MongoDB collection also removes the corresponding
    vector entries from the Atlas Vector Search index.

    Args:
        platform: Platform name (instagram, tiktok, youtube)
        document_id: MongoDB document _id as a string (preferred when available)
        username: Influencer username/handle to match against common username fields
        url: External profile URL to match against common URL fields

    Returns:
        Dict with details about the deletion outcome
    """
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

    collection = get_db().get_collection(collection_name)

    # Build the deletion filter
    delete_filter: Dict[str, Any] = {}

    if influencer_id:
        try:
            delete_filter = {"_id": ObjectId(influencer_id)}
        except Exception:
            raise ValueError(
                "Invalid influencer_id format. Must be a valid MongoDB ObjectId string."
            )

    # Execute deletion
    if "_id" in delete_filter:
        result = await collection.delete_one(delete_filter)
        deleted_count = result.deleted_count
    else:
        raise ValueError(f"Invalid influencer_id format: {influencer_id}")

    return {
        "platform": platform,
        "collection": collection_name,
        "deleted_count": int(deleted_count),
    }

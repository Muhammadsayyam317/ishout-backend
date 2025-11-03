from typing import List, Optional, Dict, Any
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from bson import ObjectId
from app.db.connection import get_db
from app.config import config

# Removed eager DB fetch to avoid initialization at import time

embeddings = None


def initialize_embeddings():
    """Initialize OpenAI embeddings with API key from centralized config"""
    global embeddings
    if embeddings is None:
        api_key = config.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OpenAI API Key not found in environment variables")
        model = config.EMBEDDING_MODEL

        # Create the embeddings client - no fallback
        embeddings = OpenAIEmbeddings(api_key=api_key, model=model)

        # Simple test to ensure embeddings work
        embeddings.embed_query("test query")

    return embeddings


def get_vector_store(collection, platform=None):
    """
    Create a vector store instance for the given collection

    Args:
        collection: MongoDB collection to use for vector storage
        platform: Platform name to determine correct field mappings

    Returns:
        MongoDBAtlasVectorSearch instance
    """
    emb = initialize_embeddings()

    # Get the index name from environment or use default (same for all platforms)
    index_name = config.MONGODB_VECTOR_INDEX_NAME

    if platform == "instagram":
        text_key = "pageContent"
    elif platform == "tiktok":
        text_key = "pageContent"
    else:
        text_key = config.MONGODB_TEXT_KEY

    embedding_key = config.MONGODB_EMBEDDING_KEY
    try:

        # Use the exact parameter order from the docs example
        vector_store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=emb,
            index_name=index_name,
            text_key=text_key,
            embedding_key=embedding_key,
        )

        print("Successfully created MongoDBAtlasVectorSearch instance")
        return vector_store

    except Exception as e:
        print(f"Error creating vector store: {str(e)}")

        try:
            vector_store = MongoDBAtlasVectorSearch(
                collection=collection, embedding=emb, index_name=index_name
            )
            return vector_store

        except Exception as e2:
            print(f"All attempts to create vector store failed: {str(e2)}")
            raise


async def query_vector_store(
    query: str,
    platform: str,
    limit: int = 10,
    min_followers: Optional[int] = None,
    max_followers: Optional[int] = None,
    country: Optional[str] = None,
) -> List[dict]:
    """Query the vector store for similar documents and return top-k results.

    This function supports pre-filtering based on follower counts and country using MongoDB Atlas
    vector search pre_filter parameter.

    Args:
        query: Search query text
        platform: Platform name (instagram, tiktok, youtube)
        limit: Maximum number of results to return
        min_followers: Minimum follower count for filtering (optional)
        max_followers: Maximum follower count for filtering (optional)
        country: Country name for filtering (optional)

    Returns:
        List of documents matching the query and filters
    """
    try:

        # Choose collection by platform
        collection_name = None
        if platform == "instagram":
            collection_name = config.MONGODB_ATLAS_COLLECTION_INSTGRAM
            collection_name = config.MONGODB_ATLAS_COLLECTION_INSTGRAM
        elif platform == "tiktok":
            collection_name = config.MONGODB_ATLAS_COLLECTION_TIKTOK
            collection_name = config.MONGODB_ATLAS_COLLECTION_TIKTOK
        elif platform == "youtube":
            collection_name = config.MONGODB_ATLAS_COLLECTION_YOUTUBE
            collection_name = config.MONGODB_ATLAS_COLLECTION_YOUTUBE
        else:
            raise ValueError(f"Invalid platform specified: {platform}")

        print(
            f"query_vector_store() - Using collection: {collection_name} for platform: {platform}"
        )
        if not collection_name:
            raise ValueError(
                f"Collection name is empty for platform {platform}. Check your environment variables."
            )

        sync_collection = get_db().get_collection(collection_name)

        store = get_vector_store(sync_collection, platform)

        try:
            limit = int(limit)
        except Exception:
            print(f"Invalid limit value provided: {limit}, falling back to 10")
            limit = 10

        # Build pre_filter based on follower and country requirements
        pre_filter = {}
        filter_conditions = []

        # Add follower filter if specified
        if min_followers is not None or max_followers is not None:
            follower_filter = {}

            if min_followers is not None and max_followers is not None:
                # Range filter: both min and max specified
                follower_filter = {"$gte": min_followers, "$lte": max_followers}
                print(f"Using follower range filter: {min_followers} - {max_followers}")
            elif min_followers is not None:
                # Only minimum specified
                follower_filter = {"$gte": min_followers}
                print(f"Using minimum follower filter: >= {min_followers}")
            elif max_followers is not None:
                # Only maximum specified
                follower_filter = {"$lte": max_followers}
                print(f"Using maximum follower filter: <= {max_followers}")

            filter_conditions.append({"followers": follower_filter})

        # Add country filter if specified
        if country:
            print(f"Using country filter: {country}")
            filter_conditions.append({"country": country})

        # Combine filters using $and if multiple conditions exist
        if len(filter_conditions) > 1:
            pre_filter = {"$and": filter_conditions}
        elif len(filter_conditions) == 1:
            pre_filter = filter_conditions[0]

        # Try to capture similarity scores where supported
        docs_with_scores = []
        try:
            if pre_filter:
                docs_with_scores = store.similarity_search_with_score(
                    query, k=limit, pre_filter=pre_filter
                )
            else:
                docs_with_scores = store.similarity_search_with_score(query, k=limit)
        except Exception:
            if pre_filter:
                docs = store.similarity_search(query, k=limit, pre_filter=pre_filter)
            else:
                docs = store.similarity_search(query, k=limit)
            docs_with_scores = [(d, None) for d in docs]

        # Convert Document objects to plain dicts and return top-k results with optional scores
        formatted_results = []
        for doc, score in docs_with_scores[:limit]:
            meta = (
                doc.metadata.copy() if hasattr(doc, "metadata") and doc.metadata else {}
            )
            meta["page_content"] = getattr(doc, "page_content", "")
            if score is not None:
                try:
                    meta["similarity_score"] = float(score)
                except Exception:
                    meta["similarity_score"] = score
            formatted_results.append(meta)
        return formatted_results

    except Exception as e:
        print(f"query_vector_store() - Error in vector search: {str(e)}")
        return []  # Return empty list instead of falling back to random docs


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
        collection_name = config.MONGODB_ATLAS_COLLECTION_INSTGRAM
        collection_name = config.MONGODB_ATLAS_COLLECTION_INSTGRAM
    elif platform == "tiktok":
        collection_name = config.MONGODB_ATLAS_COLLECTION_TIKTOK
        collection_name = config.MONGODB_ATLAS_COLLECTION_TIKTOK
    elif platform == "youtube":
        collection_name = config.MONGODB_ATLAS_COLLECTION_YOUTUBE
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

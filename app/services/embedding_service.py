import os
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings


# MongoDB connection clients
async_client: Optional[AsyncIOMotorClient] = None
sync_client: Optional[MongoClient] = None
db = None
sync_db = None
embeddings = None


def _mask_value(v: Optional[str]) -> str:
    """Mask long secret-like values for logging (don't print full URIs or keys)."""
    if v is None:
        return "<None>"
    try:
        s = str(v)
        if len(s) <= 12:
            return s
        return s[:6] + "..." + s[-6:]
    except Exception:
        return "<unrepresentable>"


async def connect_to_mongodb():
    """
    Connect to MongoDB using the credentials from environment variables
    
    Returns:
        MongoDB database instance
    """
    global async_client, sync_client, db, sync_db
    
    if not async_client:
        mongo_uri = os.getenv("MONGODB_ATLAS_URI")
        print(f"connect_to_mongodb() - MONGODB_ATLAS_URI={_mask_value(mongo_uri)}")
        if not mongo_uri:
            print("connect_to_mongodb() - MongoDB URI not found in environment variables")
            raise ValueError("MongoDB URI not found in environment variables")

        # Create both async and sync clients
        print("connect_to_mongodb() - creating AsyncIOMotorClient and MongoClient")
        async_client = AsyncIOMotorClient(mongo_uri)
        sync_client = MongoClient(mongo_uri)

        db_name = os.getenv("MONGODB_ATLAS_DB_NAME")
        print(f"connect_to_mongodb() - DB name: {db_name}")
        db = async_client[db_name]
        sync_db = sync_client[db_name]

        print("MongoDB connected (async and sync clients) ✅")
    
    return db



def initialize_embeddings():
    """Initialize OpenAI embeddings with API key from environment variables"""
    global embeddings
    if embeddings is None:
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"initialize_embeddings() - OPENAI_API_KEY present: {bool(api_key)}")
        if not api_key:
            print("initialize_embeddings() - OpenAI API Key not found in environment variables")
            raise ValueError("OpenAI API Key not found in environment variables")

        model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        print(f"initialize_embeddings() - model={model}")

        # Create the embeddings client - no fallback
        embeddings = OpenAIEmbeddings(
            api_key=api_key,
            model=model
        )

        # Simple test to ensure embeddings work
        test_embedding = embeddings.embed_query("test query")
        print(f"Embedding initialized with model {model}, dimension: {len(test_embedding)} ✅")
            
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
    # Make sure embeddings are initialized
    print(f"get_vector_store() - platform={platform}, collection_type={type(collection)}")
    emb = initialize_embeddings()
    
    # Get the index name from environment or use default
    index_name = os.getenv("MONGODB_VECTOR_INDEX_NAME", "vector_index")
    
    # Configure text_key based on platform - Instagram and TikTok use 'pageContent', YouTube uses 'text'
    if platform == "instagram":
        text_key = "pageContent"  # Instagram collection uses camelCase
        print(f"get_vector_store() - Using text_key='{text_key}' for Instagram")
    elif platform == "tiktok":
        text_key = "pageContent"  # TikTok also uses pageContent like Instagram
        print(f"get_vector_store() - Using text_key='{text_key}' for TikTok")
    else:
        text_key = os.getenv("MONGODB_TEXT_KEY", "text")  # Default for YouTube
        print(f"get_vector_store() - Using text_key='{text_key}' for platform {platform}")
    
    embedding_key = os.getenv("MONGODB_EMBEDDING_KEY", "embedding")
    print(f"get_vector_store() - embedding_key={embedding_key}")
    print(f"Creating vector store with index: {index_name}, text_key: {text_key}, embedding_key: {embedding_key}")
    
    # Following the exact format from the LangChain MongoDB docs example:
    # vector_store = MongoDBAtlasVectorSearch(
    #     collection=MONGODB_COLLECTION,
    #     embedding=embeddings,
    #     index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    #     relevance_score_fn="cosine",
    # )
    
    try:
        print(f"get_vector_store() - Creating vector store with collection type: {type(collection)}")

        # Use the exact parameter order from the docs example
        vector_store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=emb,
            index_name=index_name,
            text_key=text_key,
            embedding_key=embedding_key
        )

        print("Successfully created MongoDBAtlasVectorSearch instance")
        return vector_store

    except Exception as e:
        print(f"Error creating vector store: {str(e)}")

        # Try minimal parameters
        try:
            print("Trying minimal parameters")

            # Create with just the required parameters
            vector_store = MongoDBAtlasVectorSearch(
                collection=collection,
                embedding=emb,
                index_name=index_name
            )

            print("Successfully created vector store with minimal parameters")
            return vector_store

        except Exception as e2:
            print(f"All attempts to create vector store failed: {str(e2)}")
            raise


def parse_followers_value(followers) -> int:
    """
    Parse follower count values that may come as strings like '10K', '1.2M', '10,000'

    Returns integer follower count or 0 if it cannot be parsed.
    """
    print(f"parse_followers_value() - input={followers}")
    if followers is None:
        print("parse_followers_value() - input is None, returning 0")
        return 0

    # If already an int, return directly
    try:
        if isinstance(followers, int):
            return followers
        if isinstance(followers, float):
            return int(followers)
    except Exception:
        pass

    if isinstance(followers, str):
        s = followers.strip().replace(',', '').lower()
        try:
            # Handle values like '10k', '1.2m'
            if s.endswith('k'):
                val = int(float(s[:-1]) * 1_000)
                print(f"parse_followers_value() - parsed {followers} -> {val}")
                return val
            if s.endswith('m'):
                val = int(float(s[:-1]) * 1_000_000)
                print(f"parse_followers_value() - parsed {followers} -> {val}")
                return val
            if s.endswith('b'):
                val = int(float(s[:-1]) * 1_000_000_000)
                print(f"parse_followers_value() - parsed {followers} -> {val}")
                return val

            # Plain numeric strings
            val = int(float(s))
            print(f"parse_followers_value() - parsed {followers} -> {val}")
            return val
        except Exception:
            print(f"parse_followers_value() - Could not parse followers value: {followers}")
            return 0

    # Unknown type
    print(f"Unsupported followers type: {type(followers)}")
    return 0

async def query_vector_store(query: str, platform: str, limit: int = 10) -> List[dict]:
    """Query the vector store for similar documents and return top-k results.

    This function is intentionally lightweight: it relies on the vector index
    (and any pre-filtering defined there) to return documents matching
    metadata constraints. It is instrumented with detailed debug logs to
    help trace problems during development.
    """
    try:
        print("query_vector_store() - start")
        print(f"query_vector_store() - query={query}, platform={platform}, limit={limit}")

        # Ensure embeddings and DB connection are ready
        emb = initialize_embeddings()
        await connect_to_mongodb()

        # Choose collection by platform
        collection_name = None
        if platform == "instagram":
            collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_INSTGRAM")
        elif platform == "tiktok":
            collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_TIKTOK")
        elif platform == "youtube":
            collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_YOUTUBE")
        else:
            raise ValueError(f"Invalid platform specified: {platform}")

        print(f"query_vector_store() - Using collection: {collection_name} for platform: {platform}")
        if not collection_name:
            raise ValueError(f"Collection name is empty for platform {platform}. Check your environment variables.")

        sync_collection = sync_db[collection_name]
        print(f"query_vector_store() - sync_collection: {getattr(sync_collection, 'name', str(sync_collection))}")

        # Create vector store
        print("query_vector_store() - creating vector store")
        store = get_vector_store(sync_collection, platform)
        print(f"query_vector_store() - Vector store created successfully for collection {collection_name}")

        # Ensure limit is integer and use it directly as k for similarity search.
        try:
            limit = int(limit)
        except Exception:
            print(f"Invalid limit value provided: {limit}, falling back to 10")
            limit = 10

        # Perform the similarity search without pre_filter
        print(f"query_vector_store() - Performing vector search with k={limit} (no pre_filter)")
        try:
            docs = store.similarity_search(query, k=limit)
            print(f"query_vector_store() - Vector search returned {len(docs)} docs")
        except Exception:
            print("query_vector_store() - similarity_search failed")
            raise

        # Convert Document objects to plain dicts and return top-k results.
        formatted_results = []
        for doc in docs[:limit]:
            meta = doc.metadata.copy() if hasattr(doc, "metadata") and doc.metadata else {}
            meta["page_content"] = getattr(doc, "page_content", "")
            formatted_results.append(meta)

        # Debug: show metadata keys for returned docs (up to 3)
        for i, d in enumerate(formatted_results[:3]):
            print(f"query_vector_store() - result[{i}] keys={list(d.keys())}")

        print(f"Vector search returning {len(formatted_results)} results")
        return formatted_results

    except Exception:
        print("query_vector_store() - Error in vector search")
        return []  # Return empty list instead of falling back to random docs
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
    
    # Get the index name from environment based on platform
    if platform == "instagram":
        index_name = os.getenv("MONGODB_VECTOR_INDEX_NAME_INSTAGRAM", "vector_index_1")
    elif platform == "tiktok": 
        index_name = os.getenv("MONGODB_VECTOR_INDEX_NAME_TIKTOK", "vector_index")
    elif platform == "youtube":
        index_name = os.getenv("MONGODB_VECTOR_INDEX_NAME_YOUTUBE", "vector_index")
    else:
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

async def query_vector_store(query: str, platform: str, limit: int = 10, min_followers: Optional[int] = None, max_followers: Optional[int] = None) -> List[dict]:
    """Query the vector store for similar documents and return top-k results.

    This function supports pre-filtering based on follower counts using MongoDB Atlas
    vector search pre_filter parameter.
    
    Args:
        query: Search query text
        platform: Platform name (instagram, tiktok, youtube)
        limit: Maximum number of results to return
        min_followers: Minimum follower count for filtering (optional)
        max_followers: Maximum follower count for filtering (optional)
    
    Returns:
        List of documents matching the query and filters
    """
    try:
        print("query_vector_store() - start")
        print(f"query_vector_store() - query={query}, platform={platform}, limit={limit}")
        print(f"query_vector_store() - min_followers={min_followers}, max_followers={max_followers}")

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

        # Build pre_filter based on follower requirements
        pre_filter = {}
        if min_followers is not None or max_followers is not None:
            follower_filter = {}
            
            if min_followers is not None and max_followers is not None:
                # Range filter: both min and max specified
                follower_filter = {
                    "$gte": min_followers,
                    "$lte": max_followers
                }
                print(f"query_vector_store() - Using follower range filter: {min_followers} - {max_followers}")
            elif min_followers is not None:
                # Only minimum specified
                follower_filter = {"$gte": min_followers}
                print(f"query_vector_store() - Using minimum follower filter: >= {min_followers}")
            elif max_followers is not None:
                # Only maximum specified
                follower_filter = {"$lte": max_followers}
                print(f"query_vector_store() - Using maximum follower filter: <= {max_followers}")
            
            # Filter on the followers field at root level (based on actual data structure)
            pre_filter = {"followers": follower_filter}

        # DEBUG: Before performing search, let's check what data exists in the follower range
        if pre_filter and min_followers is not None:
            print(f"query_vector_store() - DEBUG: Checking data in follower range {min_followers}-{max_followers or 'unlimited'}")
            try:
                # Check total documents in collection
                total_docs = sync_collection.count_documents({})
                print(f"query_vector_store() - DEBUG: Total documents in collection: {total_docs}")
                
                # Check documents with followers field
                docs_with_followers = sync_collection.count_documents({"followers": {"$exists": True}})
                print(f"query_vector_store() - DEBUG: Documents with 'followers' field: {docs_with_followers}")
                
                # Check follower range distribution
                if max_followers:
                    matching_docs = sync_collection.count_documents({
                        "followers": {"$gte": min_followers, "$lte": max_followers}
                    })
                    print(f"query_vector_store() - DEBUG: Documents with followers {min_followers}-{max_followers}: {matching_docs}")
                else:
                    matching_docs = sync_collection.count_documents({
                        "followers": {"$gte": min_followers}
                    })
                    print(f"query_vector_store() - DEBUG: Documents with followers >= {min_followers}: {matching_docs}")
                
                # Show some sample follower values around our range
                pipeline = [
                    {"$match": {"followers": {"$exists": True}}},
                    {"$group": {
                        "_id": None,
                        "min_followers": {"$min": "$followers"},
                        "max_followers": {"$max": "$followers"},
                        "avg_followers": {"$avg": "$followers"}
                    }}
                ]
                stats = list(sync_collection.aggregate(pipeline))
                if stats:
                    stat = stats[0]
                    print(f"query_vector_store() - DEBUG: Follower stats - Min: {stat['min_followers']}, Max: {stat['max_followers']}, Avg: {stat['avg_followers']:.0f}")
                
                # Show a few samples near our target range
                sample_docs = list(sync_collection.find(
                    {"followers": {"$gte": min_followers * 0.8, "$lte": max_followers * 1.2 if max_followers else min_followers * 2}},
                    {"followers": 1, "name": 1, "_id": 0}
                ).limit(5))
                print(f"query_vector_store() - DEBUG: Sample docs near range: {sample_docs}")
                
            except Exception as debug_e:
                print(f"query_vector_store() - DEBUG: Error during data analysis: {str(debug_e)}")

        # Perform the similarity search with or without pre_filter
        if pre_filter:
            print(f"query_vector_store() - Performing vector search with k={limit} and pre_filter={pre_filter}")
            try:
                docs = store.similarity_search(query, k=limit, pre_filter=pre_filter)
                print(f"query_vector_store() - Vector search with filter returned {len(docs)} docs")
                
                # DEBUG: If we got 0 results, try a broader range to see if data exists
                if len(docs) == 0:
                    print(f"query_vector_store() - DEBUG: Got 0 results with pre_filter!")
                    print(f"query_vector_store() - DEBUG: This indicates the MongoDB Atlas Vector Search Index")
                    print(f"query_vector_store() - DEBUG: does NOT have 'followers' configured as a filter field.")
                    print(f"query_vector_store() - DEBUG: You need to update your Atlas Search Index configuration.")
                    
                    broader_filter = {"followers": {"$gte": min_followers * 0.5, "$lte": (max_followers or min_followers) * 2}}
                    print(f"query_vector_store() - DEBUG: Trying broader filter: {broader_filter}")
                    try:
                        broader_docs = store.similarity_search(query, k=limit, pre_filter=broader_filter)
                        print(f"query_vector_store() - DEBUG: Broader search returned {len(broader_docs)} docs")
                        if broader_docs:
                            for i, doc in enumerate(broader_docs[:3]):
                                followers = getattr(doc, 'metadata', {}).get('followers', 'N/A')
                                print(f"query_vector_store() - DEBUG: Broader result {i}: {followers} followers")
                        else:
                            print(f"query_vector_store() - DEBUG: Even broader search returned 0 results")
                            print(f"query_vector_store() - DEBUG: This CONFIRMS the index is missing filter configuration")
                    except Exception as broader_e:
                        print(f"query_vector_store() - DEBUG: Broader search also failed: {str(broader_e)}")
                        print(f"query_vector_store() - DEBUG: Error confirms index configuration issue")
                
            except Exception as e:
                print(f"query_vector_store() - similarity_search with pre_filter failed: {str(e)}")
                # Fallback to search without filter
                print("query_vector_store() - Falling back to search without pre_filter")
                docs = store.similarity_search(query, k=limit)
                print(f"query_vector_store() - Fallback search returned {len(docs)} docs")
        else:
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
            if "followers" in d:
                print(f"query_vector_store() - result[{i}] followers={d['followers']}")

        print(f"Vector search returning {len(formatted_results)} results")
        return formatted_results

    except Exception as e:
        print(f"query_vector_store() - Error in vector search: {str(e)}")
        return []  # Return empty list instead of falling back to random docs
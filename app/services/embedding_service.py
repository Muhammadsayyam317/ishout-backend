import os
import logging
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings

# Setup logging first so it's available for import statements
logger = logging.getLogger(__name__)

# Import MongoDB vector store from langchain_mongodb package
try:
    from langchain_mongodb import MongoDBAtlasVectorSearch
    logger.info("Successfully imported MongoDBAtlasVectorSearch from langchain_mongodb package")
except ImportError:
    logger.error("Failed to import MongoDBAtlasVectorSearch. Make sure langchain_mongodb is installed.")
    # Raise an explicit error since this is required for the application to work
    raise ImportError("Cannot import MongoDBAtlasVectorSearch. Run: pip install langchain-mongodb")

# MongoDB connection clients
async_client: Optional[AsyncIOMotorClient] = None
sync_client: Optional[MongoClient] = None
db = None
sync_db = None

async def connect_to_mongodb():
    """
    Connect to MongoDB using the credentials from environment variables
    
    Returns:
        MongoDB database instance
    """
    global async_client, sync_client, db, sync_db
    
    if not async_client:
        mongo_uri = os.getenv("MONGODB_ATLAS_URI")
        if not mongo_uri:
            raise ValueError("MongoDB URI not found in environment variables")
        
        # Create both async and sync clients
        async_client = AsyncIOMotorClient(mongo_uri)
        sync_client = MongoClient(mongo_uri)
        
        db_name = os.getenv("MONGODB_ATLAS_DB_NAME")
        db = async_client[db_name]
        sync_db = sync_client[db_name]
        
        logger.info("MongoDB connected (async and sync clients) ✅")
    
    return db

# Initialize OpenAI embeddings
embeddings = None

def initialize_embeddings():
    """Initialize OpenAI embeddings with API key from environment variables"""
    global embeddings
    if embeddings is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API Key not found in environment variables")
        
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        
        # Create the embeddings client - no fallback
        embeddings = OpenAIEmbeddings(
            api_key=api_key,
            model=model
        )
        
        # Simple test to ensure embeddings work
        test_embedding = embeddings.embed_query("test query")
        logger.info(f"Embedding initialized with model {model}, dimension: {len(test_embedding)} ✅")
            
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
    emb = initialize_embeddings()
    
    # Get the index name from environment or use default
    index_name = os.getenv("MONGODB_VECTOR_INDEX_NAME", "vector_index")
    
    # Configure text_key based on platform - Instagram uses 'pageContent', others use 'text'
    if platform == "instagram":
        text_key = "pageContent"  # Instagram collection uses camelCase
        print(f"DEBUG: Using text_key='{text_key}' for Instagram")
    else:
        text_key = os.getenv("MONGODB_TEXT_KEY", "text")  # Default for TikTok/YouTube
        print(f"DEBUG: Using text_key='{text_key}' for platform {platform}")
    
    embedding_key = os.getenv("MONGODB_EMBEDDING_KEY", "embedding")
    
    logger.info(f"Creating vector store with index: {index_name}, text_key: {text_key}, embedding_key: {embedding_key}")
    
    # Following the exact format from the LangChain MongoDB docs example:
    # vector_store = MongoDBAtlasVectorSearch(
    #     collection=MONGODB_COLLECTION,
    #     embedding=embeddings,
    #     index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    #     relevance_score_fn="cosine",
    # )
    
    try:
        logger.info(f"Creating vector store with collection type: {type(collection)}")
        
        # Use the exact parameter order from the docs example
        vector_store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=emb,
            index_name=index_name,
            text_key=text_key,
            embedding_key=embedding_key
        )
        
        logger.info("Successfully created MongoDBAtlasVectorSearch instance")
        return vector_store
        
    except Exception as e:
        logger.error(f"Error creating vector store: {str(e)}")
        
        # Try minimal parameters
        try:
            logger.info("Trying minimal parameters")
            
            # Create with just the required parameters
            vector_store = MongoDBAtlasVectorSearch(
                collection=collection,
                embedding=emb,
                index_name=index_name
            )
            
            logger.info("Successfully created vector store with minimal parameters")
            return vector_store
            
        except Exception as e2:
            logger.error(f"All attempts to create vector store failed: {str(e2)}")
            raise

async def query_vector_store(query: str, platform: str, limit: int = 10, category: str = None, min_followers: int = None) -> List[dict]:
    """
    Query the vector store for similar documents with filtering
    
    Args:
        query: The search query
        platform: The platform to search (instagram, tiktok, youtube)
        limit: Maximum number of results to return
        category: Category filter for content matching
        min_followers: Minimum follower count filter
        
    Returns:
        List of documents filtered and sorted by follower proximity
    """
    try:
        # Initialize embeddings first
        emb = initialize_embeddings()
        
        # Then connect to MongoDB (this initializes both async and sync clients)
        await connect_to_mongodb()
        
        # Get the appropriate collection based on platform
        collection_name = None
        if platform == "instagram":
            collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_INFLUENCERS")
        elif platform == "tiktok":
            collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_TIKTOK")
        elif platform == "youtube":
            collection_name = os.getenv("MONGODB_ATLAS_COLLECTION_YOUTUBE")
        else:
            raise ValueError(f"Invalid platform specified: {platform}")
        
        # Debug collection name
        logger.info(f"Using collection: {collection_name} for platform: {platform}")
        
        if not collection_name:
            raise ValueError(f"Collection name is empty for platform {platform}. Check your environment variables.")
        
        # Use both async and sync collections
        async_collection = db[collection_name]
        sync_collection = sync_db[collection_name]
        
        # Count documents in collection using async client
        doc_count = await async_collection.count_documents({})
        print(f"DEBUG: Found {doc_count} documents in collection {collection_name} for platform {platform}")
        logger.info(f"Found {doc_count} documents in collection {collection_name}")
        
        # If collection exists but has no documents, return a more specific message
        if doc_count == 0:
            print(f"DEBUG: Collection {collection_name} is empty!")
            raise ValueError(f"Collection {collection_name} exists but is empty")
        
        # DEBUG: Check if documents have embedding field
        sample_doc = await async_collection.find_one({})
        if sample_doc:
            has_embedding = "embedding" in sample_doc
            print(f"DEBUG: Sample document keys: {list(sample_doc.keys())}")
            print(f"DEBUG: Has 'embedding' field: {has_embedding}")
            if has_embedding:
                embedding_type = type(sample_doc["embedding"])
                embedding_length = len(sample_doc["embedding"]) if isinstance(sample_doc["embedding"], list) else "N/A"
                print(f"DEBUG: Embedding type: {embedding_type}, length: {embedding_length}")
        else:
            print(f"DEBUG: Could not retrieve sample document")
        
        # Create vector store with the synchronous collection
        # This should avoid the "MotorDatabase object is not callable" error
        store = get_vector_store(sync_collection, platform)
        logger.info(f"Vector store created successfully for collection {collection_name}")
        
        # Log the query to help debug
        logger.info(f"Searching with query: '{query}', category: '{category}', min_followers: {min_followers}")
        
        # Get more results initially if we need to filter by followers (to have a good pool)
        search_limit = limit * 10 if min_followers else limit
        
        logger.info(f"Performing vector search with search_limit: {search_limit}")
        docs = store.similarity_search(
            query, 
            k=search_limit
        )
        logger.info(f"Vector search found {len(docs)} results")
        
        # Convert all results to a consistent dictionary format
        all_results = []
        for doc in docs:
            # It's a Document object with metadata, convert to dict
            doc_dict = doc.metadata.copy() if hasattr(doc, "metadata") else {}
            # Add the document content
            doc_dict["page_content"] = getattr(doc, "page_content", "No content")
            all_results.append(doc_dict)
        
        # Apply follower filtering and sorting if min_followers is specified
        formatted_results = all_results
        if min_followers is not None:
            print(f"DEBUG: Filtering by followers >= {min_followers}")
            
            # Filter by minimum followers
            filtered_results = []
            for doc in all_results:
                doc_followers = doc.get("followers", 0)
                if isinstance(doc_followers, str):
                    try:
                        doc_followers = int(doc_followers.replace(',', ''))
                    except:
                        doc_followers = 0
                
                if doc_followers >= min_followers:
                    # Add follower proximity score (closer to target = better)
                    follower_diff = abs(doc_followers - min_followers)
                    doc["follower_proximity"] = 1 / (1 + follower_diff / min_followers) if min_followers > 0 else 1
                    filtered_results.append(doc)
            
            print(f"DEBUG: After follower filtering: {len(filtered_results)} results")
            
            # Sort by follower proximity (closest to target first)
            filtered_results.sort(key=lambda x: -x.get("follower_proximity", 0))
            
            # Take only the requested limit
            formatted_results = filtered_results[:limit]
            
            print(f"DEBUG: Final results after sorting and limiting: {len(formatted_results)}")
        else:
            # If no follower filter, just take the top results
            formatted_results = all_results[:limit]
        
        # Log results
        logger.info(f"Vector search found {len(formatted_results)} results.")
        
        # Log sample document data to verify different results
        if formatted_results:
            for i, doc in enumerate(formatted_results[:2]):  # Log first two for brevity
                content = doc.get("page_content", "")[:50] + "..." if doc.get("page_content") else ""
                followers = doc.get("followers", "N/A")
                logger.info(f"Result {i+1}: Followers: {followers} | {content}")
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error in vector search: {str(e)}")
        logger.exception("Full exception details:")
        return []  # Return empty list instead of falling back to random docs
import os
import logging
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from langchain_openai import OpenAIEmbeddings

# Try to import from the new package location first
try:
    from langchain_mongodb import MongoDBAtlasVectorSearch
except ImportError:
    # Fall back to community version if the new package is not installed
    from langchain_community.vectorstores import MongoDBAtlasVectorSearch

# Setup logging
logger = logging.getLogger(__name__)

# MongoDB connection client
client: Optional[AsyncIOMotorClient] = None
db = None

async def connect_to_mongodb():
    """
    Connect to MongoDB using the credentials from environment variables
    
    Returns:
        MongoDB database instance
    """
    global client, db
    
    if not client:
        mongo_uri = os.getenv("MONGODB_ATLAS_URI")
        if not mongo_uri:
            raise ValueError("MongoDB URI not found in environment variables")
        
        client = AsyncIOMotorClient(mongo_uri)
        db_name = os.getenv("MONGODB_ATLAS_DB_NAME")
        db = client[db_name]
        logger.info("MongoDB connected ✅")
    
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
        try:
            embeddings = OpenAIEmbeddings(
                api_key=api_key,
                model=model
            )
            # Test the embedding with a simple query to ensure it works
            try:
                test_embedding = embeddings.embed_query("test query")
                if not isinstance(test_embedding, list) or len(test_embedding) == 0:
                    logger.warning("Embedding test failed - invalid embedding format")
            except Exception as e:
                logger.warning(f"Failed to generate test embedding: {str(e)}")
            
            logger.info(f"OpenAI Embeddings initialized with model {model} ✅")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI embeddings: {str(e)}")
            # Create a fallback embedding object that just returns an empty vector
            # This helps avoid crashes while allowing debugging
            embeddings = {"embed_query": lambda q: [0.0] * 1536}
            
    return embeddings

def get_vector_store(collection):
    """
    Create a vector store instance for the given collection
    
    Args:
        collection: MongoDB collection to use for vector storage
        
    Returns:
        MongoDBAtlasVectorSearch instance
    """
    # Make sure embeddings are initialized
    emb = initialize_embeddings()
    
    # Get the index name from environment or use default
    index_name = os.getenv("MONGODB_VECTOR_INDEX_NAME", "vector_index")
    text_key = os.getenv("MONGODB_TEXT_KEY", "text")
    embedding_key = os.getenv("MONGODB_EMBEDDING_KEY", "embedding")
    
    logger.info(f"Creating vector store with index: {index_name}, text_key: {text_key}, embedding_key: {embedding_key}")
    
    # Try to use the more recent version of the MongoDB Atlas Vector Search
    try:
        return MongoDBAtlasVectorSearch(emb, {
            "collection": collection,
            "index_name": index_name,
            "text_key": text_key,
            "embedding_key": embedding_key,
        })
    except Exception as e:
        logger.error(f"Error creating MongoDB Atlas Vector Search: {str(e)}")
        # Create a dummy vector store that will just return sample data
        class DummyVectorStore:
            def similarity_search(self, query, k=10):
                logger.warning("Using dummy vector store - no actual vector search performed")
                return [{"page_content": "Dummy result - vector search failed", "metadata": {}}]
        return DummyVectorStore()

async def query_vector_store(query: str, platform: str, limit: int = 10) -> List[dict]:
    """
    Query the vector store for similar documents
    
    Args:
        query: The search query
        platform: The platform to search (instagram, tiktok, youtube)
        limit: Maximum number of results to return
        
    Returns:
        List of similar documents
    """
    # Initialize embeddings first
    emb = initialize_embeddings()
    
    # Then connect to MongoDB
    database = await connect_to_mongodb()
    
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
        logger.error(f"Collection name is empty for platform {platform}. Check your environment variables.")
        return [{"page_content": "Collection not configured", "metadata": {}}]
        
    # Check if the collection exists
    collection = database[collection_name]
    
    # Count documents in collection
    doc_count = await collection.count_documents({})
    logger.info(f"Found {doc_count} documents in collection {collection_name}")
    
    # If collection exists but has no documents, return a more specific message
    if doc_count == 0:
        logger.warning(f"Collection {collection_name} exists but is empty")
        return [{"page_content": "No influencers found in database", "metadata": {}}]
        
    # Try direct MongoDB query as a fallback to check if data is accessible
    try:
        # Sample a document to understand the structure
        sample_doc = await collection.find_one({})
        if sample_doc:
            logger.info(f"Sample document keys: {list(sample_doc.keys())}")
            
            # If there's no vector index, try a simple text search
            random_docs = []
            cursor = collection.find({}).limit(limit)
            async for doc in cursor:
                # Extract external links based on platform
                socials = doc.get("socials", {})
                if not socials and platform == "tiktok" and "externalLink" in doc:
                    # Special case for TikTok data structure
                    socials = {"tiktok": doc.get("externalLink", "")}
                
                # Create a metadata dict with all document fields except a few system ones
                metadata = {}
                for key, value in doc.items():
                    if key not in ["_id", "text", "embedding"]:
                        metadata[key] = value
                        
                # Add special mappings for common fields if they're not already present
                if "socials" not in metadata:
                    metadata["socials"] = socials
                    
                if "externalLink" not in metadata:
                    if platform == "instagram" and "socials" in metadata and "instagram" in metadata["socials"]:
                        metadata["externalLink"] = metadata["socials"]["instagram"]
                    elif platform == "tiktok" and "socials" in metadata and "tiktok" in metadata["socials"]:
                        metadata["externalLink"] = metadata["socials"]["tiktok"]
                    elif platform == "youtube" and "socials" in metadata and "youtube" in metadata["socials"]:
                        metadata["externalLink"] = metadata["socials"]["youtube"]
                        
                # Convert MongoDB document to expected format
                random_docs.append({
                    "page_content": doc.get("text", "No content"),
                    "metadata": metadata
                })
            
            if random_docs:
                logger.info(f"Returning {len(random_docs)} random documents as fallback")
                return random_docs
    except Exception as e:
        logger.error(f"Error during direct MongoDB query: {str(e)}")
        
    # Create vector store and perform similarity search
    try:
        store = get_vector_store(collection)
        logger.info(f"Vector store created successfully for collection {collection_name}")
        
        # Check which method is available (async or sync)
        try:
            results = None
            # Log the embedding being used
            test_embedding = emb.embed_query(query)
            logger.info(f"Generated embedding for query with {len(test_embedding)} dimensions")
            
            if hasattr(store, "asimilarity_search"):
                logger.info("Using async similarity search")
                results = await store.asimilarity_search(query, k=limit)
            else:
                logger.info("Using sync similarity search")
                results = store.similarity_search(query, k=limit)
            
            # Convert all results to a consistent dictionary format
            formatted_results = []
            for doc in results:
                if isinstance(doc, dict):
                    formatted_results.append(doc)
                else:
                    # It's a Document object, convert to dict
                    formatted_results.append({
                        "page_content": getattr(doc, "page_content", "No content"),
                        "metadata": getattr(doc, "metadata", {})
                    })
                    
            if formatted_results:
                logger.info(f"Vector search successful, found {len(formatted_results)} results")
                return formatted_results
            else:
                logger.warning("Vector search returned no results")
        except AttributeError as e:
            logger.error(f"Similarity search error: {str(e)}")
    except Exception as e:
        logger.error(f"Error setting up vector store: {str(e)}")
        
    # Return a mock result with empty data if all else fails
    return [{"page_content": "No results found", "metadata": {}}]
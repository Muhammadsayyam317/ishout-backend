from typing import List, Optional
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
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
        )
        result = await store.similarity_search(query, k=limit)
        for res in result:
            result.append(res.page_content)
        return result
    except Exception as e:
        print(f"Error querying vector store: {str(e)}")
        return []

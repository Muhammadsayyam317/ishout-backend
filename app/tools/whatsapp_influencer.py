from typing import List
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from app.config import config
from app.db.connection import get_pymongo_db


def find_influencers_for_whatsapp(
    platform: str,
    category: str,
    limit: int,
    country: str,
    followers: str,
) -> List[dict]:
    query = f"Find {limit} {category} influencers on {platform} in {country } followers {followers}".strip()
    print(f"[find_influencers_for_whatsapp] Query: {query}")
    try:
        collection_name = None
        text_key = None
        if platform.lower() == "instagram":
            collection_name = config.MONGODB_ATLAS_COLLECTION_INSTAGRAM
            text_key = "pageContent"

        elif platform.lower() == "tiktok":
            collection_name = config.MONGODB_ATLAS_COLLECTION_TIKTOK
            text_key = "pageContent"

        elif platform.lower() == "youtube":
            collection_name = config.MONGODB_ATLAS_COLLECTION_YOUTUBE
            text_key = "text"

        else:
            raise ValueError(f"Invalid platform specified: {platform}")
        if not collection_name:
            raise ValueError(
                f"Collection name is empty for platform {platform}. Check your environment variables."
            )
        collection = get_pymongo_db()[collection_name]
        print(f"[find_influencers_for_whatsapp] Using collection: {collection_name}")
        embeddings = OpenAIEmbeddings(
            api_key=config.OPENAI_API_KEY,
            model=config.EMBEDDING_MODEL,
        )
        store = MongoDBAtlasVectorSearch(
            collection=collection,
            embedding=embeddings,
            index_name=f"embedding_index_{platform}",
            text_key=text_key,
            embedding_key="embedding",
            relevance_score_fn="cosine",
        )
        print(f"[find_influencers_for_whatsapp] Query: {query}")
        docs = store.similarity_search(query, k=limit)
        result = [doc.page_content for doc in docs]
        return result

    except Exception as e:
        print(f"Error finding influencers for WhatsApp: {str(e)}")
        return []

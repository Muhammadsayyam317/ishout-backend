#!/usr/bin/env python3
"""
MongoDB Atlas Vector Search Index Configuration Helper

This script helps diagnose and fix the MongoDB Atlas Vector Search Index configuration.
The issue is that your index doesn't have 'followers' configured as a filter field.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_index_configuration():
    """Check the current search index configuration"""
    
    print("="*80)
    print("MongoDB Atlas Vector Search Index Configuration Check")
    print("="*80)
    
    mongo_uri = os.getenv("MONGODB_ATLAS_URI")
    db_name = os.getenv("MONGODB_ATLAS_DB_NAME")
    
    client = AsyncIOMotorClient(mongo_uri)
    db = client[db_name]
    
    collections = ["instagram", "tiktok", "youtube"]
    
    for collection_name in collections:
        print(f"\n📋 Checking {collection_name.upper()} collection:")
        print("-" * 50)
        
        collection = db[collection_name]
        
        try:
            # Try to get search indexes (this might not work with motor, but let's try)
            indexes = await collection.list_search_indexes()
            print(f"✅ Search indexes found: {len(indexes)}")
            
            async for index in indexes:
                print(f"Index name: {index.get('name', 'unnamed')}")
                print(f"Index status: {index.get('status', 'unknown')}")
                
        except Exception as e:
            print(f"❌ Cannot check search indexes via code: {str(e)}")
            print("💡 This is normal - you need to check manually in Atlas UI")
        
        # Check data structure 
        sample_doc = await collection.find_one({})
        if sample_doc and 'followers' in sample_doc:
            print(f"✅ Data has 'followers' field: {sample_doc['followers']}")
        else:
            print(f"❌ Data missing 'followers' field")
    
    client.close()
    
    print(f"\n" + "="*80)
    print("🔧 HOW TO FIX THE INDEX CONFIGURATION")
    print("="*80)
    
    print("""
🎯 PROBLEM: Your MongoDB Atlas Vector Search Index is missing the 'followers' filter field.

📋 SOLUTION: Update your Atlas Search Index configuration

🔗 STEPS TO FIX:
1. Go to MongoDB Atlas Dashboard (https://cloud.mongodb.com)
2. Navigate to your cluster → Search tab  
3. Find your search index (probably named 'vector_index')
4. Click "Edit" button
5. Replace the JSON configuration with this:

{
  "fields": [
    {
      "numDimensions": 1536,
      "path": "embedding",
      "similarity": "cosine", 
      "type": "vector"
    },
    {
      "path": "followers",
      "type": "filter"
    }
  ]
}

6. Click "Save" and wait for re-indexing to complete
7. Test your filtering again

⚠️  IMPORTANT: 
- You need to do this for ALL three collections (instagram, tiktok, youtube)
- Each collection needs its own search index with the filter field
- Re-indexing may take a few minutes depending on data size

✅ VERIFICATION:
After updating, your follower filtering should work perfectly!
    """)

if __name__ == "__main__":
    asyncio.run(check_index_configuration())
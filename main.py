
import os
import sys
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.embedding_service import connect_to_mongodb

# Prevent Python from writing bytecode files
sys.dont_write_bytecode = True
# Load environment variables
load_dotenv()


# Create FastAPI app
app = FastAPI(
    title="Ishout API",
    description="API for finding social media influencers",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=False,  # Wildcard origins cannot be used with credentials
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.api.api import api_router
app.include_router(api_router)



if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port,
        reload=False,
    )
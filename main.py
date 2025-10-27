
import os
import sys
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from app.services.embedding_service import connect_to_mongodb

# Prevent Python from writing bytecode files
sys.dont_write_bytecode = True
# Load environment variables
load_dotenv()

# Create security scheme for Swagger UI
security = HTTPBearer(
    scheme_name="Bearer",
    description="Enter your Bearer token",
    auto_error=False
)

# Security scheme for OpenAPI documentation
security_schemes = {
    "Bearer": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Enter your JWT token"
    }
}

# Create FastAPI app
app = FastAPI(
    title="Ishout API",
    description="API for finding social media influencers",
    version="1.0.0",
    swagger_ui_init_oauth={
        "clientId": "swagger-ui",
    },
    swagger_ui_parameters={
        "persistAuthorization": True,
    }
)

# Add security schemes to OpenAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = security_schemes
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

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
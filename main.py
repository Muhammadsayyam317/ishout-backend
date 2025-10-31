import os
from app.db.connection import (
    close,
    connect,
)
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from app.api.api import api_router
from contextlib import asynccontextmanager

security = HTTPBearer(
    scheme_name="Bearer", description="Enter your Bearer token", auto_error=False
)

# Security scheme for OpenAPI documentation
security_schemes = {
    "Bearer": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Enter your JWT token",
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
    },
)


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect()
    yield
    close()


app.lifespan = lifespan

app.include_router(api_router)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )

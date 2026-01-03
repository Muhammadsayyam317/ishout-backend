from app.core.redis import init_redis_agent
from app.db.connection import connect, close
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from app.api.api import api_router
from contextlib import asynccontextmanager
from app.core.errors import register_exception_handlers


security = HTTPBearer(
    scheme_name="Bearer", description="Enter your Bearer token", auto_error=False
)
security_schemes = {
    "Bearer": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Enter your JWT token",
    }
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()
    print("connected successfully")
    await init_redis_agent(app)
    yield
    await close()
    print("🧹closed")


app = FastAPI(
    title="Ishout API",
    description="API for finding social media influencers",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_init_oauth={"clientId": "swagger-ui"},
    swagger_ui_parameters={"persistAuthorization": True},
)
register_exception_handlers(app)


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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ishout.vercel.app",
        "http://localhost:3000",
        "https://backend.ishout.ae",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

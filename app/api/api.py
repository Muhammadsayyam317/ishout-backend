from fastapi import APIRouter

# Direct import of the router from the chat_routes module
from app.api.routes.chat_routes import router as chat_router

# Main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(chat_router, prefix="/api", tags=["chat"])
from fastapi import APIRouter

from app.api.routes.chat_routes import router as chat_router
from app.api.routes.auth_routes import router as auth_router
from app.api.routes.admin_routes import router as admin_router
from app.api.routes.meta_routes import router as meta_router

api_router = APIRouter()
api_router.include_router(chat_router, prefix="/api")
api_router.include_router(auth_router, prefix="/api/auth")
api_router.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
api_router.include_router(meta_router, prefix="/api/meta", tags=["Meta"])

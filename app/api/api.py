from fastapi import APIRouter

# Import all route modules
from app.api.routes.chat_routes import router as chat_router
from app.api.routes.auth_routes import router as auth_router
from app.api.routes.admin_routes import router as admin_router
from app.api.routes.meta_routes import router as meta_router
from app.api.routes.ws_routes import router as ws_router
from app.api.routes.notify_routes import router as notify_router

# Main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(chat_router, prefix="/api")
api_router.include_router(auth_router, prefix="/api/auth")
api_router.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
api_router.include_router(meta_router, prefix="/api/meta", tags=["Meta"])
api_router.include_router(ws_router, prefix="/api/ws", tags=["WebSockets"])
api_router.include_router(notify_router, tags=["Notifications"])

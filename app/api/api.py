from fastapi import APIRouter

from app.api.routes.company_routes import router as company_router
from app.api.routes.admin_routes import router as admin_router
from app.api.routes.meta_routes import router as meta_router
from app.api.routes.ws_routes import router as ws_router
from app.api.routes.auth_routes import router as auth_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
api_router.include_router(company_router, prefix="/api/company", tags=["Company"])
api_router.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
api_router.include_router(meta_router, prefix="/api/meta", tags=["Meta"])
api_router.include_router(ws_router, prefix="/api/ws", tags=["WebSocket"])

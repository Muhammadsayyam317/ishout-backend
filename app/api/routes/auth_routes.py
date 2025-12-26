from fastapi import APIRouter, BackgroundTasks
from app.Schemas.user_model import (
    CompanyRegistrationRequest,
    UserLoginRequest,
)
from app.api.controllers.auth.login import login_user
from app.api.controllers.auth.register import register_company
from fastapi import HTTPException

router = APIRouter()


@router.post("/register", tags=["Auth"])
async def register_route(
    request_data: CompanyRegistrationRequest,
    background_tasks: BackgroundTasks,
):
    try:
        return await register_company(request_data, background_tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", tags=["Auth"])
async def login_route(request_data: UserLoginRequest):
    try:
        return await login_user(request_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

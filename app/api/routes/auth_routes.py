from fastapi import APIRouter, BackgroundTasks
from app.Schemas.user_model import (
    CompanyRegistrationRequest,
    UserLoginRequest,
)

from app.api.controllers.auth.auth_controller import login_user, register_company
from app.core.exception import InternalServerErrorException

router = APIRouter()


@router.post("/register", tags=["Auth"])
async def register_route(
    request_data: CompanyRegistrationRequest,
    background_tasks: BackgroundTasks,
):
    try:
        return await register_company(request_data, background_tasks)
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e


@router.post("/login", tags=["Auth"])
async def login_route(request_data: UserLoginRequest):
    try:
        return await login_user(request_data)
    except Exception as e:
        raise InternalServerErrorException(message=str(e)) from e

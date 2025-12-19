from app.api.controllers.company.profile import get_user_profile, update_user_profile
from app.api.controllers.auth_controller import change_password
from fastapi import APIRouter

router = APIRouter()

router.add_api_route(
    path="/update-profile/{user_id}",
    endpoint=update_user_profile,
    methods=["PUT"],
    tags=["User"],
)

router.add_api_route(
    path="/user-profile/{user_id}",
    endpoint=get_user_profile,
    methods=["GET"],
    tags=["User"],
)

router.add_api_route(
    path="/change-password",
    endpoint=change_password,
    methods=["PUT"],
    tags=["User"],
)

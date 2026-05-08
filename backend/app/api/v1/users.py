from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.services.user_service import build_current_user_response


router = APIRouter(prefix="/api/v1/users", tags=["users-v1"])


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return build_current_user_response(current_user)
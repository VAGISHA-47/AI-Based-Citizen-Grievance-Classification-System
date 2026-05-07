from fastapi import APIRouter

from app.models.schemas import Token, UserCreate, UserLogin
from app.services.auth_service import build_login_response, build_registration_response


router = APIRouter(prefix="/api/v1/auth", tags=["auth-v1"])


@router.post("/register")
async def register(user: UserCreate):
    return build_registration_response(user)


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    return build_login_response(user)
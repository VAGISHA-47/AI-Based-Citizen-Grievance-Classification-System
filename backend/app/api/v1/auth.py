from fastapi import APIRouter

from app.models.schemas import AuthLoginRequest, AuthLoginResponse, UserCreate
from app.services.auth_service import build_registration_response
from app.services.supabase_service import login_user


router = APIRouter(prefix="/api/v1/auth", tags=["auth-v1"])


@router.post("/register")
async def register(user: UserCreate):
    return build_registration_response(user)


@router.post("/login", response_model=AuthLoginResponse)
async def login(user: AuthLoginRequest):
    return login_user(user.phone, user.password)
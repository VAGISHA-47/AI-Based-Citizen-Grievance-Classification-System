from fastapi import APIRouter, HTTPException
from app.models.schemas import UserCreate, UserLogin, Token
from app.utils.auth import hash_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(user: UserCreate):
    """Temporary registration endpoint (no DB persistence yet)."""
    # Hash the password before persisting (DB integration later)
    hashed = hash_password(user.password)

    # NOTE: Do not persist to database here. Database integration will be
    # added by the database teammate.
    return {
        "message": "User registration endpoint ready",
        "email": user.email,
        "note": "Database persistence will be integrated later",
    }


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Temporary login endpoint that issues a JWT token (no DB verification yet)."""
    # In a real implementation, verify the user's credentials against the DB.
    token = create_access_token({"sub": user.email, "role": "citizen"})
    return {"access_token": token, "token_type": "bearer"}

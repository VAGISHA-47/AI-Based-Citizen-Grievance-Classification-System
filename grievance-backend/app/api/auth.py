from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models.schemas import UserCreate, UserLogin, Token
from app.utils.auth import create_access_token, verify_token

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 scheme for extracting bearer token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


@router.post("/register")
async def register(user: UserCreate):
    """Temporary registration endpoint (no DB persistence yet)."""
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


@router.get("/me")
async def me(token: str = Depends(oauth2_scheme)):
    """Return authenticated user's email if the provided JWT is valid."""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Prefer 'sub' claim, fall back to 'email' if present
    email = payload.get("sub") or payload.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"email": email, "status": "authenticated"}

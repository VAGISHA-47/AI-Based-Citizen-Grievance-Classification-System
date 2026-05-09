from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from app.utils.auth import verify_token

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 scheme for extracting bearer token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register")
async def register(payload: dict):
    """Temporary registration endpoint accepting both email and phone payloads."""
    name = payload.get("name", "User")
    phone = payload.get("phone")
    email = payload.get("email")
    password = payload.get("password")

    if not password or (not phone and not email):
        raise HTTPException(status_code=422, detail="phone/email and password are required")

    return {
        "message": "User registration endpoint ready",
        "name": name,
        "phone": phone,
        "email": email,
        "note": "Database persistence will be integrated later",
    }


@router.post("/auth/login")
@router.post("/login")
async def login(request: Request):
    body = await request.json()

    # Accept both phone and email fields
    identifier = body.get("phone") or body.get("email") or ""
    password = body.get("password", "")

    from app.db.supabase_client import supabase
    from app.utils.auth import verify_password, create_access_token

    # Search by email first, then phone
    result = supabase.table("users").select("*").eq("email", identifier).execute()
    if not result.data:
        result = supabase.table("users").select("*").eq("phone", identifier).execute()

    if not result.data:
        raise HTTPException(status_code=401, detail="User not found")

    user = result.data[0]

    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({"sub": user["email"] or user["phone"], "role": user["role"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"],
        "name": user["name"],
        "user_id": str(user["user_id"])
    }


@router.get("/me")
async def get_me(token: str = Depends(oauth2_scheme)):
    """Return authenticated user's identity if the provided JWT is valid."""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {"email": email, "status": "authenticated"}

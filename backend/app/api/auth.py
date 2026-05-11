from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from app.utils.auth import verify_token, verify_password, hash_password

router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2 scheme for extracting bearer token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register")
async def register(request: Request):
    try:
        body = await request.json()
        from app.db.supabase_client import supabase

        phone = str(body.get("phone", "")).strip()
        email = str(body.get("email", "")).strip()
        name = str(body.get("name", "User")).strip()
        password = str(body.get("password", "")).strip()

        if not phone and not email:
            raise HTTPException(
                status_code=400,
                detail="Phone or email is required"
            )

        if not password:
            raise HTTPException(
                status_code=400,
                detail="Password is required"
            )

        # Check if user already exists
        if phone:
            existing = supabase.table("users").select(
                "user_id"
            ).eq("phone", phone).execute()
            if existing.data:
                raise HTTPException(
                    status_code=400,
                    detail="User with this phone already exists"
                )

        # Insert only safe columns
        insert_data = {
            "name": name or "User",
            "password_hash": hash_password(password),
            "role": "citizen",
            "trust_score": 50,
            "trust_level": "new",
            "is_verified": False,
            "language_pref": "hi",
        }

        if phone:
            insert_data["phone"] = phone
        if email:
            insert_data["email"] = email

        result = supabase.table("users").insert(
            insert_data
        ).execute()

        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Registration failed"
            )

        return {
            "message": "Registration successful",
            "user_id": str(result.data[0]["user_id"])
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[REGISTER ERROR] {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Registration error: {str(e)}"
        )


@router.post("/auth/login")
@router.post("/login")
async def login(request: Request):
    body = await request.json()

    # Accept both phone and email fields
    identifier = body.get("phone") or body.get("email") or ""
    password = body.get("password", "")

    from app.db.supabase_client import supabase
    from app.utils.auth import create_access_token

    # Search by email first, then by phone (simple two-step lookup)
    result = supabase.table("users").select("*").eq("email", identifier).execute()
    if not result.data:
        result = supabase.table("users").select("*").eq("phone", identifier).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="User not found")

    user = result.data[0]

    # Verify password; on failure, return generic message as well
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

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

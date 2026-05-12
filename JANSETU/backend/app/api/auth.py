from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer

from app.utils.auth import create_access_token, hash_password, verify_password, verify_token

router = APIRouter(prefix="/auth", tags=["auth"])
router_v1 = APIRouter(prefix="/api/v1/auth", tags=["auth-v1"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def _supabase():
    from app.db.supabase_client import supabase
    return supabase


def _lookup_user(identifier: str) -> dict | None:
    sb = _supabase()
    # Try phone first, then email
    r = sb.table("users").select("*").eq("phone", identifier).execute()
    if not r.data:
        r = sb.table("users").select("*").eq("email", identifier).execute()
    return r.data[0] if r.data else None


def _build_response(user: dict) -> dict:
    user_id = str(user.get("user_id") or "")
    token_payload = {
        "sub": user_id or user.get("phone") or user.get("email") or "",
        "role": user.get("role", "citizen"),
        "user_id": user_id,
        "phone": user.get("phone", ""),
    }
    access_token = create_access_token(token_payload)
    # Real schema uses ward_id (not assigned_ward_id)
    data = {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.get("role", "citizen"),
        "name": user.get("name", "User"),
        "user_id": user_id,
        "jurisdiction_assigned": bool(user.get("ward_id") or user.get("assigned_ward_id")),
    }
    return {"success": True, **data, "data": data}


async def _register(payload: dict) -> dict:
    sb = _supabase()
    phone = payload.get("phone", "")
    email = payload.get("email", "")
    name = payload.get("name", "Citizen")
    password = payload.get("password", "")

    if not password or (not phone and not email):
        raise HTTPException(status_code=422, detail="phone/email and password are required")

    existing = None
    if phone:
        existing = sb.table("users").select("user_id").eq("phone", phone).execute()
    if not existing or not existing.data:
        if email:
            existing = sb.table("users").select("user_id").eq("email", email).execute()
    if existing and existing.data:
        raise HTTPException(status_code=400, detail="User already exists")

    result = sb.table("users").insert({
        "phone": phone,
        "email": email or f"{phone}@jansetu.in",
        "name": name,
        "password_hash": hash_password(password),
        "role": "citizen",
        "trust_score": 50,
        "trust_level": "new",
        "is_verified": False,
    }).execute()

    if not result or not result.data:
        raise HTTPException(status_code=500, detail="Registration failed")

    return {"message": "User registered successfully", "user_id": str(result.data[0]["user_id"])}


async def _login(request: Request, officer_only: bool = False) -> dict:
    body = await request.json()
    identifier = body.get("phone") or body.get("email") or ""
    password = body.get("password", "")

    if not identifier or not password:
        raise HTTPException(status_code=422, detail="phone/email and password are required")

    user = _lookup_user(identifier)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    pw_hash = user.get("password_hash", "")
    if not pw_hash:
        raise HTTPException(status_code=401, detail="Account has no password set")

    if not verify_password(password, pw_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if officer_only and user.get("role") not in ("officer", "admin"):
        raise HTTPException(status_code=403, detail="Access denied. Officer credentials required.")

    return _build_response(user)


async def _me(token: str) -> dict:
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub") or payload.get("user_id")
    role = payload.get("role", "citizen")

    try:
        sb = _supabase()
        r = sb.table("users").select("*").eq("user_id", user_id).execute()
        if r.data:
            u = r.data[0]
            return {
                "user_id": str(u.get("user_id") or ""),
                "name": u.get("name", "User"),
                "phone": u.get("phone", ""),
                "email": u.get("email", ""),
                "role": u.get("role", role),
                "trust_score": u.get("trust_score", 50),
                "trust_level": u.get("trust_level", "new"),
                "is_verified": u.get("is_verified", False),
            }
    except Exception:
        pass

    return {"sub": user_id, "role": role, "status": "authenticated"}


# ── Legacy /auth/* ─────────────────────────────────────────────────────────

@router.post("/register")
async def register(payload: dict):
    return await _register(payload)


@router.post("/login")
async def login(request: Request):
    return await _login(request)


@router.get("/me")
async def get_me(token: str = Depends(oauth2_scheme)):
    return await _me(token)


# ── V1 /api/v1/auth/* ─────────────────────────────────────────────────────

@router_v1.post("/register")
async def register_v1(payload: dict):
    return await _register(payload)


@router_v1.post("/login")
async def login_v1(request: Request):
    return await _login(request)


@router_v1.post("/officer-login")
async def officer_login_v1(request: Request):
    return await _login(request, officer_only=True)


@router_v1.get("/me")
async def get_me_v1(token: str = Depends(oauth2_scheme)):
    return await _me(token)

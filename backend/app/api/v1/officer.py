from fastapi import APIRouter, Depends, Header, HTTPException

from app.models.schemas import OfficerJurisdictionUpdateRequest
from app.services.officer_service import build_officer_queue_response, build_officer_summary_response
from app.services.supabase_service import get_officer_profile_by_user, update_officer_jurisdiction
from app.utils.auth import verify_token


router = APIRouter(prefix="/api/v1/officers", tags=["officer-v1"])


async def _current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    payload = verify_token(authorization.removeprefix("Bearer ").strip())
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


@router.get("/me/queue")
async def get_my_queue(current_user: dict = Depends(_current_user)):
    if current_user.get("role") not in {"officer", "senior_officer", "admin"}:
        raise HTTPException(status_code=403, detail="Officer role required")
    return build_officer_queue_response()


@router.get("/analytics/summary")
async def analytics_summary(current_user: dict = Depends(_current_user)):
    if current_user.get("role") not in {"officer", "senior_officer", "admin"}:
        raise HTTPException(status_code=403, detail="Officer role required")
    return build_officer_summary_response()


@router.get("/me")
async def get_me(current_user: dict = Depends(_current_user)):
    profile = get_officer_profile_by_user(current_user.get("sub", ""))
    if not profile or not profile.get("officer_id"):
        raise HTTPException(status_code=404, detail="Officer profile not found")
    return profile


@router.patch("/me/jurisdiction")
async def save_jurisdiction(
    payload: OfficerJurisdictionUpdateRequest,
    current_user: dict = Depends(_current_user),
):
    if current_user.get("role") not in {"officer", "senior_officer", "admin"}:
        raise HTTPException(status_code=403, detail="Officer role required")
    try:
        return update_officer_jurisdiction(current_user.get("sub", ""), payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
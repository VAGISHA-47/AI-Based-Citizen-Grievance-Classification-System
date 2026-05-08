from fastapi import APIRouter, Depends, Header, HTTPException

from app.models.schemas import ComplaintCreateRequest, ComplaintStatusUpdateRequest
from app.services.supabase_service import create_complaint, get_complaint_by_tracking_token, update_complaint_status
from app.utils.auth import verify_token


router = APIRouter(prefix="/api/v1/complaints", tags=["complaints-v1"])


async def _current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    payload = verify_token(authorization.removeprefix("Bearer ").strip())
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


@router.post("")
async def post_complaint(payload: ComplaintCreateRequest, current_user: dict = Depends(_current_user)):
    citizen_phone = current_user.get("sub", "")
    citizen_name = current_user.get("name") or "Citizen"
    return create_complaint(payload, citizen_name, citizen_phone, officer_id=current_user.get("officer_id"))


@router.get("/{tracking_token}")
async def get_complaint(tracking_token: str):
    complaint = get_complaint_by_tracking_token(tracking_token)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@router.get("/my")
async def my_complaints(current_user: dict = Depends(_current_user)):
    # Placeholder fallback for citizen dashboard integration.
    # In Supabase mode, this can be replaced with a filtered citizen query.
    return []


@router.patch("/{complaint_id}/status")
async def patch_complaint_status(
    complaint_id: str,
    payload: ComplaintStatusUpdateRequest,
    current_user: dict = Depends(_current_user),
):
    if current_user.get("role") not in {"officer", "senior_officer", "admin"}:
        raise HTTPException(status_code=403, detail="Officer role required")
    return update_complaint_status(complaint_id, payload.status, payload.note, current_user.get("sub", ""))

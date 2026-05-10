from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status

from app.api.dependencies import require_role
from app.api.grievances import _resolve_user_id
from app.db.supabase_client import supabase
from app.models.schemas import ComplaintCreateRequest, ComplaintStatusUpdateRequest
from app.services.ai_pipeline import classify_text
from app.services.geo_mapper import get_ward_from_coordinates
from app.services.routing_engine import run_routing_engine
from app.services.sla_service import calculate_sla
from app.services.token_generator import generate_tracking_token


router = APIRouter(prefix="/api/v1/complaints", tags=["complaints"])

_COMPLAINT_CACHE: dict[str, dict[str, Any]] = {}
_COMPLAINT_TIMELINES: dict[str, list[dict[str, str]]] = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _store_complaint_snapshot(record: dict[str, Any]) -> None:
    complaint_id = str(record.get("complaint_id") or record.get("id") or "")
    tracking_token = str(record.get("tracking_token") or "")
    if complaint_id:
        _COMPLAINT_CACHE[complaint_id] = record
    if tracking_token:
        _COMPLAINT_CACHE[tracking_token] = record


def _append_timeline_entry(key: str, status_value: str, note: str = "", created_at: str | None = None) -> None:
    if not key:
        return
    timeline = _COMPLAINT_TIMELINES.setdefault(key, [])
    timeline.append(
        {
            "status": status_value,
            "note": note or "",
            "created_at": created_at or _now_iso(),
        }
    )


def _serialize_user(user_row: dict[str, Any] | None) -> dict[str, Any] | None:
    if not user_row:
        return None
    return {
        "user_id": user_row.get("user_id"),
        "name": user_row.get("name") or "Citizen",
        "email": user_row.get("email"),
        "phone": user_row.get("phone"),
        "role": user_row.get("role") or "citizen",
        "trust_score": user_row.get("trust_score"),
        "trust_level": user_row.get("trust_level"),
        "is_verified": user_row.get("is_verified"),
    }


def _load_user_by_id(user_id: str | None) -> dict[str, Any] | None:
    if not user_id:
        return None
    try:
        result = supabase.table("users").select("*").eq("user_id", user_id).limit(1).execute()
        if result.data:
            return result.data[0]
    except Exception:
        return None
    return None


def _load_officer_by_id(officer_id: str | None) -> dict[str, Any] | None:
    if not officer_id:
        return None
    try:
        result = supabase.table("officers").select("*").eq("officer_id", officer_id).limit(1).execute()
        if result.data:
            return result.data[0]
    except Exception:
        return None
    return None


def _build_ai_analysis(complaint_row: dict[str, Any], snapshot: dict[str, Any] | None) -> dict[str, Any]:
    snapshot = snapshot or {}
    return {
        "category": complaint_row.get("category") or snapshot.get("category") or "General",
        "predicted_category": snapshot.get("predicted_category") or complaint_row.get("category") or "General",
        "priority": complaint_row.get("priority") or snapshot.get("priority") or "medium",
        "sla_days": complaint_row.get("sla_days") or snapshot.get("sla_days") or 5.0,
        "confidence": complaint_row.get("ai_confidence") or snapshot.get("confidence") or 0.0,
        "language": snapshot.get("language") or "English",
        "address": snapshot.get("address") or complaint_row.get("address") or "",
        "media_urls": snapshot.get("media_urls") or [],
    }


def _build_timeline(complaint_row: dict[str, Any], complaint_key: str | None, snapshot: dict[str, Any] | None) -> list[dict[str, str]]:
    snapshot = snapshot or {}
    timeline: list[dict[str, str]] = []
    created_at = complaint_row.get("created_at") or snapshot.get("created_at")
    timeline.append(
        {
            "status": "submitted",
            "note": "Complaint submitted",
            "created_at": created_at or _now_iso(),
        }
    )

    assigned_at = complaint_row.get("assigned_at") or snapshot.get("assigned_at")
    if complaint_row.get("officer_id") or snapshot.get("officer_id"):
        timeline.append(
            {
                "status": "assigned",
                "note": "Complaint assigned to an officer",
                "created_at": assigned_at or created_at or _now_iso(),
            }
        )

    current_status = str(complaint_row.get("status") or snapshot.get("status") or "submitted")
    if current_status.lower() not in {"submitted", "assigned"}:
        timeline.append(
            {
                "status": current_status,
                "note": complaint_row.get("resolution_text") or snapshot.get("note") or "Status updated",
                "created_at": complaint_row.get("resolved_at") or complaint_row.get("updated_at") or _now_iso(),
            }
        )

    cached_timeline = _COMPLAINT_TIMELINES.get(complaint_key or "", [])
    if cached_timeline:
        timeline.extend(cached_timeline)

    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in timeline:
        marker = (item.get("status", ""), item.get("note", ""), item.get("created_at", ""))
        if marker in seen:
            continue
        seen.add(marker)
        deduped.append(item)
    return deduped


def _fetch_complaint_by_tracking_token(tracking_token: str) -> dict[str, Any] | None:
    try:
        result = supabase.table("complaints").select("*").eq("tracking_token", tracking_token).limit(1).execute()
        if result.data:
            return result.data[0]
    except Exception:
        return None
    return None


def _fetch_complaint_by_id(complaint_id: str) -> dict[str, Any] | None:
    try:
        result = supabase.table("complaints").select("*").eq("complaint_id", complaint_id).limit(1).execute()
        if result.data:
            return result.data[0]
    except Exception:
        return None
    return None


async def _create_complaint(
    payload: ComplaintCreateRequest,
    request: Request,
    background_tasks: BackgroundTasks | None = None,
) -> dict[str, Any]:
    text = payload.text.strip()
    normalized_text = text or payload.category or "General complaint"
    ai_result = classify_text(normalized_text)
    complaint_category = payload.category or ai_result.get("category") or "General"
    priority = str(ai_result.get("priority") or "Medium").upper()
    sla_days = calculate_sla(complaint_category, priority)
    ward = get_ward_from_coordinates(payload.lat, payload.lng)
    tracking_token = generate_tracking_token(complaint_category, ward)
    auth_header = request.headers.get("authorization")
    user_id = _resolve_user_id(auth_header, "", "Citizen")

    duplicate_status = {"is_duplicate": False}
    if text:
        try:
            from app.services.duplicate_service import check_duplicate

            duplicate_status = check_duplicate(text, complaint_category)
        except Exception:
            duplicate_status = {"is_duplicate": False}

    duplicate_warning = duplicate_status if duplicate_status.get("is_duplicate") else None

    insert_payload = {
        "user_id": user_id,
        "tracking_token": tracking_token,
        "text_original": text,
        "category": complaint_category,
        "priority": priority.lower(),
        "sla_days": sla_days,
        "ai_confidence": 0.0,
        "lat": float(payload.lat),
        "lng": float(payload.lng),
        "status": "submitted",
    }

    result = supabase.table("complaints").insert(insert_payload).execute()
    complaint_row = result.data[0] if result.data else None
    if not complaint_row:
        complaint_row = _fetch_complaint_by_tracking_token(tracking_token)
    if not complaint_row:
        raise HTTPException(status_code=500, detail="Complaint insert did not return a record")

    complaint_id = str(complaint_row.get("complaint_id") or complaint_row.get("id") or "")
    snapshot = {
        "complaint_id": complaint_id,
        "tracking_token": tracking_token,
        "text": text,
        "category": complaint_category,
        "priority": priority,
        "sla_days": sla_days,
        "language": payload.language,
        "address": payload.address,
        "media_urls": list(payload.media_urls or []),
        "predicted_category": ai_result.get("category") or complaint_category,
        "confidence": 0.0,
        "created_at": complaint_row.get("created_at") or _now_iso(),
        "status": complaint_row.get("status") or "submitted",
        "user_id": user_id,
        "duplicate": bool(duplicate_warning),
        "duplicate_similarity": duplicate_warning.get("similarity") if duplicate_warning else 0.0,
        "duplicate_match": duplicate_warning.get("matched_complaint") if duplicate_warning else None,
    }
    _store_complaint_snapshot({**complaint_row, **snapshot})
    _append_timeline_entry(complaint_id or tracking_token, "submitted", "Complaint submitted", snapshot["created_at"])

    if background_tasks is not None and complaint_id:
        background_tasks.add_task(
            run_routing_engine,
            complaint_id,
            {
                "description": text,
                "category": complaint_category,
                "priority": priority,
                "sla_days": sla_days,
                "sentiment": "Neutral",
                "citizen_name": "Citizen",
                "citizen_phone": "",
                "lat": payload.lat,
                "lng": payload.lng,
                "media_urls": list(payload.media_urls or []),
                "auth_score": 0.0,
            },
        )

    return {
        "complaint_id": complaint_id,
        "tracking_token": tracking_token,
        "sla_days": sla_days,
        "status": complaint_row.get("status") or "submitted",
        "duplicate": bool(duplicate_warning),
    }


@router.post("")
@router.post("/")
async def create_complaint(payload: ComplaintCreateRequest, request: Request, background_tasks: BackgroundTasks):
    return await _create_complaint(payload, request, background_tasks)


@router.get("/{tracking_token}")
async def get_complaint(tracking_token: str):
    complaint_row = _fetch_complaint_by_tracking_token(tracking_token)
    snapshot = _COMPLAINT_CACHE.get(tracking_token) or {}

    if not complaint_row and not snapshot:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if not complaint_row:
        complaint_row = snapshot

    complaint_id = str(complaint_row.get("complaint_id") or complaint_row.get("id") or snapshot.get("complaint_id") or "")
    if complaint_id and not snapshot:
        snapshot = _COMPLAINT_CACHE.get(complaint_id) or snapshot

    citizen_row = _load_user_by_id(str(complaint_row.get("user_id") or snapshot.get("user_id") or ""))
    officer_row = _load_officer_by_id(str(complaint_row.get("officer_id") or snapshot.get("officer_id") or ""))
    ai_analysis = _build_ai_analysis(complaint_row, snapshot)
    timeline = _build_timeline(complaint_row, complaint_id or tracking_token, snapshot)

    complaint_payload = dict(complaint_row)
    complaint_payload.setdefault("tracking_token", tracking_token)
    complaint_payload.setdefault("complaint_id", complaint_id)

    return {
        **complaint_payload,
        "complaint": complaint_payload,
        "citizen": _serialize_user(citizen_row) or snapshot.get("citizen") or {"name": "Citizen"},
        "ai_analysis": ai_analysis,
        "officer": officer_row or snapshot.get("officer"),
        "timeline": timeline,
        "status_timeline": timeline,
    }


@router.patch("/{complaint_id}/status")
async def update_complaint_status(
    complaint_id: str,
    payload: ComplaintStatusUpdateRequest,
    current_user: dict[str, Any] = Depends(require_role("officer", "admin")),
):
    complaint_row = _fetch_complaint_by_id(complaint_id)
    if not complaint_row:
        raise HTTPException(status_code=404, detail="Complaint not found")

    update_payload: dict[str, Any] = {"status": payload.status}
    if payload.note:
        update_payload["resolution_text"] = payload.note
    if payload.status.lower() in {"resolved", "closed", "completed"}:
        update_payload["resolved_at"] = "now()"

    result = supabase.table("complaints").update(update_payload).eq("complaint_id", complaint_id).execute()
    updated_row = result.data[0] if result.data else {**complaint_row, **update_payload}

    complaint_key = str(updated_row.get("complaint_id") or complaint_id)
    _store_complaint_snapshot(updated_row)
    _append_timeline_entry(complaint_key, payload.status, payload.note or "Status updated")

    return {
        "complaint_id": complaint_key,
        "status": payload.status,
        "note": payload.note,
        "updated_by": current_user.get("id"),
    }
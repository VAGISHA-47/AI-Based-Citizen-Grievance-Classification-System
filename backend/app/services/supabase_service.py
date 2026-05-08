from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.db.supabase import get_supabase_client
from app.models.schemas import ComplaintCreateRequest, OfficerJurisdictionUpdateRequest
from app.utils.auth import create_access_token, verify_password


_SAMPLE_PASSWORD_CITIZEN = "plain:password123"
_SAMPLE_PASSWORD_OFFICER = "plain:officer123"

_SAMPLE_STATES = [
    {"state_id": 1, "state_name": "Madhya Pradesh", "state_code": "MP"},
    {"state_id": 2, "state_name": "Maharashtra", "state_code": "MH"},
]

_SAMPLE_DISTRICTS = [
    {"district_id": 1, "district_name": "Bhopal", "state_id": 1},
    {"district_id": 2, "district_name": "Indore", "state_id": 1},
    {"district_id": 3, "district_name": "Mumbai", "state_id": 2},
]

_SAMPLE_AREAS = [
    {"area_id": 1, "area_name": "Kolar", "district_id": 1, "pincode": "462042"},
    {"area_id": 2, "area_name": "Arera Colony", "district_id": 1, "pincode": "462016"},
    {"area_id": 3, "area_name": "Vijay Nagar", "district_id": 2, "pincode": "452010"},
]

_SAMPLE_WARDS = [
    {"ward_id": 1, "ward_number": "12", "ward_name": "Kolar Main Ward", "area_id": 1},
    {"ward_id": 2, "ward_number": "8", "ward_name": "Arera Central Ward", "area_id": 2},
    {"ward_id": 3, "ward_number": "21", "ward_name": "Vijay Nagar East Ward", "area_id": 3},
]

_SAMPLE_OFFICERS = [
    {
        "officer_id": "off-1001",
        "badge_number": "BADGE-1001",
        "name": "Inspector Ramesh Kumar",
        "email": "ramesh.kumar@jansetu.gov.in",
        "phone": "9000000001",
        "role": "officer",
        "assigned_ward_id": 1,
        "additional_ward_ids": [2],
        "district_id": 1,
        "jurisdiction_assigned": True,
        "password_hash": _SAMPLE_PASSWORD_OFFICER,
    },
    {
        "officer_id": "off-2001",
        "badge_number": "BADGE-2001",
        "name": "Senior Officer Anika Sen",
        "email": "anika.sen@jansetu.gov.in",
        "phone": "9000000002",
        "role": "senior_officer",
        "assigned_ward_id": None,
        "additional_ward_ids": [],
        "district_id": 1,
        "jurisdiction_assigned": False,
        "password_hash": _SAMPLE_PASSWORD_OFFICER,
    },
]

_SAMPLE_CITIZENS = [
    {
        "citizen_id": "cit-1001",
        "name": "Rahul Sharma",
        "phone": "9876543210",
        "email": "rahul.sharma@example.com",
        "password_hash": _SAMPLE_PASSWORD_CITIZEN,
    },
]

_SAMPLE_AUTH_USERS = [
    {
        "auth_user_id": "user-cit-1001",
        "phone": "9876543210",
        "email": "rahul.sharma@example.com",
        "password_hash": _SAMPLE_PASSWORD_CITIZEN,
        "role": "citizen",
        "citizen_id": "cit-1001",
        "officer_id": None,
        "is_active": True,
    },
    {
        "auth_user_id": "user-off-1001",
        "phone": "9000000001",
        "email": "ramesh.kumar@jansetu.gov.in",
        "password_hash": _SAMPLE_PASSWORD_OFFICER,
        "role": "officer",
        "citizen_id": None,
        "officer_id": "off-1001",
        "is_active": True,
    },
    {
        "auth_user_id": "user-off-2001",
        "phone": "9000000002",
        "email": "anika.sen@jansetu.gov.in",
        "password_hash": _SAMPLE_PASSWORD_OFFICER,
        "role": "senior_officer",
        "citizen_id": None,
        "officer_id": "off-2001",
        "is_active": True,
    },
]

_SAMPLE_COMPLAINTS: dict[str, dict[str, Any]] = {}
_SAMPLE_TIMELINES: dict[str, list[dict[str, Any]]] = {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _password_matches(stored_password: str, candidate_password: str) -> bool:
    if stored_password.startswith("plain:"):
        return stored_password.removeprefix("plain:") == candidate_password
    return verify_password(candidate_password, stored_password)


def _supabase():
    return get_supabase_client()


def _rows_or_sample(table_name: str, sample_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    client = _supabase()
    if not client:
        return deepcopy(sample_rows)
    try:
        response = client.table(table_name).select("*").execute()
        rows = response.data or []
        return rows if rows else deepcopy(sample_rows)
    except Exception:
        return deepcopy(sample_rows)


def list_states() -> list[dict[str, Any]]:
    return _rows_or_sample("states", _SAMPLE_STATES)


def list_districts(state_id: int) -> list[dict[str, Any]]:
    client = _supabase()
    if client:
        try:
            response = client.table("districts").select("district_id,district_name,state_id").eq("state_id", state_id).order("district_name").execute()
            rows = response.data or []
            if rows:
                return rows
        except Exception:
            pass
    return [row for row in deepcopy(_SAMPLE_DISTRICTS) if row["state_id"] == state_id]


def list_areas(district_id: int) -> list[dict[str, Any]]:
    client = _supabase()
    if client:
        try:
            response = client.table("areas").select("area_id,area_name,district_id,pincode").eq("district_id", district_id).order("area_name").execute()
            rows = response.data or []
            if rows:
                return rows
        except Exception:
            pass
    return [row for row in deepcopy(_SAMPLE_AREAS) if row["district_id"] == district_id]


def list_wards(area_id: int) -> list[dict[str, Any]]:
    client = _supabase()
    if client:
        try:
            response = client.table("wards").select("ward_id,ward_number,ward_name,area_id").eq("area_id", area_id).order("ward_number").execute()
            rows = response.data or []
            if rows:
                return rows
        except Exception:
            pass
    return [row for row in deepcopy(_SAMPLE_WARDS) if row["area_id"] == area_id]


def _find_auth_user(identifier: str) -> dict[str, Any] | None:
    client = _supabase()
    if client:
        try:
            response = client.table("auth_users").select("*").or_(f"phone.eq.{identifier},email.eq.{identifier}").limit(1).execute()
            rows = response.data or []
            if rows:
                return rows[0]
        except Exception:
            pass

    for user in _SAMPLE_AUTH_USERS:
        if identifier in {user["phone"], user["email"]}:
            return deepcopy(user)
    for officer in _SAMPLE_OFFICERS:
        if identifier in {officer["badge_number"], officer["email"], officer["phone"]}:
            linked = next((u for u in _SAMPLE_AUTH_USERS if u["officer_id"] == officer["officer_id"]), None)
            return deepcopy(linked) if linked else None
    return None


def _load_officer_profile(officer_id: str | None) -> dict[str, Any] | None:
    if not officer_id:
        return None
    client = _supabase()
    if client:
        try:
            response = client.table("officers").select("*").eq("officer_id", officer_id).limit(1).execute()
            rows = response.data or []
            if rows:
                officer = rows[0]
                officer["jurisdiction_assigned"] = bool(officer.get("assigned_ward_id"))
                return officer
        except Exception:
            pass
    officer = next((row for row in _SAMPLE_OFFICERS if row["officer_id"] == officer_id), None)
    return deepcopy(officer) if officer else None


def login_user(phone: str, password: str) -> dict[str, Any]:
    auth_user = _find_auth_user(phone)
    if auth_user and _password_matches(auth_user["password_hash"], password):
        role = auth_user["role"]
        display_name = "Citizen"
        assigned_ward_id = None
        officer_id = auth_user.get("officer_id")
        jurisdiction_assigned = False

        if role == "citizen":
            citizen_id = auth_user.get("citizen_id")
            citizen = next((row for row in _SAMPLE_CITIZENS if row["citizen_id"] == citizen_id), None)
            display_name = citizen["name"] if citizen else auth_user.get("email", "Citizen")
        else:
            officer = _load_officer_profile(officer_id)
            if officer:
                display_name = officer.get("name", auth_user.get("email", "Officer"))
                assigned_ward_id = officer.get("assigned_ward_id")
                jurisdiction_assigned = bool(assigned_ward_id)
                role = officer.get("role", role)

        token_payload = {
            "sub": auth_user.get("email") or auth_user.get("phone") or phone,
            "role": role,
            "user_id": auth_user.get("auth_user_id"),
        }
        access_token = create_access_token(token_payload)
        refresh_token = create_access_token({**token_payload, "type": "refresh"})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": auth_user.get("auth_user_id"),
            "role": role,
            "name": display_name,
            "jurisdiction_assigned": jurisdiction_assigned,
            "assigned_ward_id": assigned_ward_id,
            "officer_id": officer_id,
        }

    fallback_role = "citizen"
    if phone.lower().startswith("badge-") or "@" in phone or phone.startswith("officer"):
        fallback_role = "officer"
    token_payload = {"sub": phone, "role": fallback_role, "user_id": f"mock-{phone}"}
    return {
        "access_token": create_access_token(token_payload),
        "refresh_token": create_access_token({**token_payload, "type": "refresh"}),
        "user_id": f"mock-{phone}",
        "role": fallback_role,
        "name": "Officer" if fallback_role != "citizen" else "Citizen",
        "jurisdiction_assigned": fallback_role == "citizen",
        "assigned_ward_id": 1 if fallback_role == "citizen" else None,
        "officer_id": "off-1001" if fallback_role != "citizen" else None,
    }


def get_officer_profile_by_user(phone: str) -> dict[str, Any]:
    auth_user = _find_auth_user(phone)
    if auth_user and auth_user.get("officer_id"):
        officer = _load_officer_profile(auth_user["officer_id"])
        if officer:
            return {
                "officer_id": officer["officer_id"],
                "badge_number": officer.get("badge_number"),
                "name": officer.get("name", "Officer"),
                "email": officer.get("email"),
                "role": officer.get("role", "officer"),
                "assigned_ward_id": officer.get("assigned_ward_id"),
                "additional_ward_ids": officer.get("additional_ward_ids", []),
                "district_id": officer.get("district_id"),
                "jurisdiction_assigned": bool(officer.get("assigned_ward_id")),
            }
    return {
        "officer_id": "",
        "badge_number": None,
        "name": "Officer",
        "email": None,
        "role": "officer",
        "assigned_ward_id": None,
        "additional_ward_ids": [],
        "district_id": None,
        "jurisdiction_assigned": False,
    }


def update_officer_jurisdiction(phone: str, payload: OfficerJurisdictionUpdateRequest) -> dict[str, Any]:
    auth_user = _find_auth_user(phone)
    officer_id = auth_user.get("officer_id") if auth_user else None
    if not officer_id:
        raise ValueError("Officer account not found")

    client = _supabase()
    additional = list(dict.fromkeys(payload.additional_ward_ids or []))
    if client:
        try:
            officer_update = {
                "assigned_ward_id": payload.ward_id,
                "additional_ward_ids": additional,
                "updated_at": _utc_now(),
            }
            client.table("officers").update(officer_update).eq("officer_id", officer_id).execute()
            client.table("jurisdiction_mappings").insert(
                [
                    {"officer_id": officer_id, "ward_id": payload.ward_id, "is_primary": True},
                    *[
                        {"officer_id": officer_id, "ward_id": ward_id, "is_primary": False}
                        for ward_id in additional
                    ],
                ]
            ).execute()
        except Exception:
            pass

    for officer in _SAMPLE_OFFICERS:
        if officer["officer_id"] == officer_id:
            officer["assigned_ward_id"] = payload.ward_id
            officer["additional_ward_ids"] = additional
            officer["jurisdiction_assigned"] = True
            officer["updated_at"] = _utc_now()
            break

    return get_officer_profile_by_user(phone)


def create_complaint(payload: ComplaintCreateRequest, citizen_name: str, citizen_phone: str, officer_id: str | None = None) -> dict[str, Any]:
    tracking_token = f"JST-{uuid4().hex[:8].upper()}"
    complaint_id = str(uuid4())
    record = {
        "complaint_id": complaint_id,
        "tracking_token": tracking_token,
        "citizen_name": citizen_name,
        "citizen_phone": citizen_phone,
        "officer_id": officer_id,
        "ward_id": None,
        "category": payload.category,
        "text": payload.text,
        "language": payload.language,
        "lat": payload.lat,
        "lng": payload.lng,
        "address": payload.address,
        "media_urls": payload.media_urls,
        "ai_analysis": {
            "category": payload.category,
            "priority": "medium",
            "confidence": 0.74,
            "sentiment": "neutral",
            "note": "AI analysis placeholder until pipeline is connected",
        },
        "status": "pending",
        "sla_days": 7,
        "created_at": _utc_now(),
        "updated_at": _utc_now(),
    }

    client = _supabase()
    if client:
        try:
            client.table("complaints").insert(record).execute()
            client.table("complaint_status_timeline").insert(
                {
                    "complaint_id": complaint_id,
                    "status": "pending",
                    "note": "Complaint created",
                }
            ).execute()
        except Exception:
            pass

    _SAMPLE_COMPLAINTS[tracking_token] = record
    _SAMPLE_TIMELINES[tracking_token] = [
        {"status": "pending", "note": "Complaint created", "created_at": record["created_at"]},
    ]

    return {
        "complaint_id": complaint_id,
        "tracking_token": tracking_token,
        "sla_days": 7,
        "status": "pending",
    }


def get_complaint_by_tracking_token(tracking_token: str) -> dict[str, Any] | None:
    client = _supabase()
    if client:
        try:
            response = client.table("complaints").select("*").eq("tracking_token", tracking_token).limit(1).execute()
            rows = response.data or []
            if rows:
                complaint = rows[0]
                timeline_response = client.table("complaint_status_timeline").select("status,note,created_at").eq("complaint_id", complaint["complaint_id"]).order("created_at").execute()
                timeline = timeline_response.data or []
                return {
                    "complaint_id": complaint["complaint_id"],
                    "tracking_token": complaint["tracking_token"],
                    "citizen": {
                        "name": complaint.get("citizen_name"),
                        "phone": complaint.get("citizen_phone"),
                    },
                    "officer": {
                        "officer_id": complaint.get("officer_id"),
                        "name": "Assigned Officer",
                    } if complaint.get("officer_id") else None,
                    "complaint": complaint,
                    "ai_analysis": complaint.get("ai_analysis", {}),
                    "status_timeline": timeline,
                }
        except Exception:
            pass

    complaint = _SAMPLE_COMPLAINTS.get(tracking_token)
    if not complaint:
        return None
    return {
        "complaint_id": complaint["complaint_id"],
        "tracking_token": complaint["tracking_token"],
        "citizen": {"name": complaint.get("citizen_name"), "phone": complaint.get("citizen_phone")},
        "officer": {"officer_id": complaint.get("officer_id"), "name": "Assigned Officer"} if complaint.get("officer_id") else None,
        "complaint": complaint,
        "ai_analysis": complaint.get("ai_analysis", {}),
        "status_timeline": _SAMPLE_TIMELINES.get(tracking_token, []),
    }


def update_complaint_status(complaint_id: str, status: str, note: str, officer_phone: str) -> dict[str, Any]:
    client = _supabase()
    officer = _find_auth_user(officer_phone)
    officer_id = officer.get("officer_id") if officer else None
    if client:
        try:
            client.table("complaints").update({"status": status, "updated_at": _utc_now()}).eq("complaint_id", complaint_id).execute()
            client.table("complaint_status_timeline").insert(
                {
                    "complaint_id": complaint_id,
                    "status": status,
                    "note": note,
                    "changed_by": officer_id,
                }
            ).execute()
        except Exception:
            pass

    for tracking_token, complaint in _SAMPLE_COMPLAINTS.items():
        if complaint["complaint_id"] == complaint_id:
            complaint["status"] = status
            complaint["updated_at"] = _utc_now()
            _SAMPLE_TIMELINES.setdefault(tracking_token, []).append(
                {"status": status, "note": note, "created_at": _utc_now()}
            )
            return {"complaint_id": complaint_id, "status": status, "note": note}

    return {"complaint_id": complaint_id, "status": status, "note": note}

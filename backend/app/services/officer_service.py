"""Placeholder officer service helpers for the v1 scaffold."""

import logging

logger = logging.getLogger(__name__)

# Static mapping of complaint categories to assigned officer IDs
DEPT_OFFICERS = {
    "Water Supply": ["officer_w1", "officer_w2", "officer_w3"],
    "Roads": ["officer_r1", "officer_r2"],
    "Electricity": ["officer_e1", "officer_e2"],
    "Health": ["officer_h1", "officer_h2"],
}


def build_officer_queue_response() -> dict:
    return {
        "message": "Officer queue endpoint ready",
        "officer_id": "mock-officer-id",
        "grievances": [],
        "note": "Database query will be integrated later",
    }


def build_officer_summary_response() -> dict:
    return {
        "message": "Officer analytics summary endpoint ready",
        "summary": {
            "total_assigned": 0,
            "pending": 0,
            "in_progress": 0,
            "resolved": 0,
            "overdue": 0,
        },
        "by_category": [],
        "note": "Real analytics aggregation will be integrated later",
    }


async def assign_least_loaded_officer(category: str, ward: str) -> str:
    from app.db.supabase_client import supabase

    officers = DEPT_OFFICERS.get(category, ["officer_general"])

    min_load = float("inf")
    selected = officers[0]

    try:
        for officer_id in officers:
            result = supabase.table("complaints").select(
                "complaint_id", count="exact"
            ).eq("officer_id", officer_id).in_(
                "status", ["assigned", "in_progress"]
            ).execute()
            count = result.count or 0
            if count < min_load:
                min_load = count
                selected = officer_id
    except Exception as e:
        print(f"[OFFICER] Supabase query failed: {e}")

    return selected
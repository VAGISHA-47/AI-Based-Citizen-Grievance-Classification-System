from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/officer", tags=["officer"])


@router.get("/assigned")
async def get_assigned_complaints():
    from app.db.supabase_client import supabase
    try:
        result = supabase.table("complaints").select(
            "complaint_id, tracking_token, text_original,"
            "category, priority, status, created_at,"
            "lat, lng, address, sla_days, sla_deadline,"
            "officer_id, ai_confidence"
        ).order("created_at", desc=True).limit(50).execute()
        return result.data or []
    except Exception as e:
        print(f"[OFFICER] get_assigned error: {e}")
        return []


@router.get("/complaints/count")
async def get_complaints_count():
    from app.db.supabase_client import supabase
    try:
        result = supabase.table("complaints").select(
            "complaint_id", count="exact"
        ).execute()
        return {"total": result.count or 0}
    except Exception:
        return {"total": 0}


@router.patch("/{complaint_id}/resolve")
async def resolve_complaint(complaint_id: str, request: Request):
    from app.db.supabase_client import supabase
    from datetime import datetime, timezone
    try:
        body = {}
        try:
            body = await request.json()
        except Exception:
            pass
        resolution = body.get(
            "resolution", "Resolved by officer"
        )

        supabase.table("complaints").update({
            "status": "resolved",
            "resolution_text": resolution,
            "resolved_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }).eq("complaint_id", complaint_id).execute()
        return {
            "message": "Complaint resolved",
            "complaint_id": complaint_id,
            "status": "resolved"
        }
    except Exception as e:
        print(f"[RESOLVE ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/summary")
async def analytics_summary():
    from app.db.supabase_client import supabase

    result = supabase.table("complaints").select("category, status").execute()
    return result.data

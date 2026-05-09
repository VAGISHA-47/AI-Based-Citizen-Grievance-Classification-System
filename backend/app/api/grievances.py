from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException

from app.services.routing_engine import run_routing_engine
from app.services.geo_mapper import get_ward_from_coordinates
from app.services.token_generator import generate_tracking_token


router = APIRouter(prefix="/grievances", tags=["grievances"])
TEMP_COMPLAINTS: dict[str, dict] = {}


@router.post("/")
async def submit_grievance(
    title: str = Form(...),
    description: str = Form(...),
    channel: str = Form("web"),
    lat: float = Form(...),
    lng: float = Form(...),
    citizen_name: str = Form(...),
    citizen_phone: str = Form(...),
    address: str = Form(""),
    file: UploadFile | None = File(None),
    background_tasks: BackgroundTasks = None,
):
    """Submit a citizen grievance and route it through the processing pipeline."""
    ward = get_ward_from_coordinates(float(lat), float(lng))
    tracking_token = generate_tracking_token(title or "General", ward)

    try:
        from app.db.supabase_client import supabase

        result = supabase.table("complaints").insert({
            "tracking_token": tracking_token,
            "text_original": description,
            "category": title,
            "lat": float(lat),
            "lng": float(lng),
            "status": "submitted",
        }).execute()

        grievance_id = result.data[0]["complaint_id"]
    except Exception as e:
        # Fallback if Supabase unavailable
        print(f"Warning: Failed to save to Supabase: {str(e)}")
        grievance_id = f"temp-{uuid4()}"
        TEMP_COMPLAINTS[tracking_token] = {
            "complaint_id": grievance_id,
            "tracking_token": tracking_token,
            "title": title,
            "text_original": description,
            "category": title,
            "status": "submitted",
            "lat": float(lat),
            "lng": float(lng),
        }
    
    # Queue the routing engine as a background task
    if background_tasks is not None:
        background_tasks.add_task(
            run_routing_engine,
            grievance_id,
            {
                "description": description,
                "category": "",                    # will be filled by AI
                "priority": "MEDIUM",              # default
                "sentiment": "Neutral",
                "citizen_name": citizen_name,
                "citizen_phone": citizen_phone,
                "lat": lat,
                "lng": lng,
                "media_urls": [],                  # from uploaded file if any
                "auth_score": 0.0
            }
        )

    return {
        "message": "Grievance submitted",
        "status": "processing",
        "grievance_id": grievance_id,
        "tracking_token": tracking_token,
    }


@router.get("/track/{token}")
async def track_complaint(token: str):
    from app.db.supabase_client import supabase

    result = supabase.table("complaints").select("*").eq("tracking_token", token).execute()
    if result.data:
        return result.data[0]

    temp = TEMP_COMPLAINTS.get(token)
    if temp:
        return temp

    raise HTTPException(status_code=404, detail="Complaint not found")


@router.get("/my")
async def my_complaints():
    from app.db.supabase_client import supabase

    result = supabase.table("complaints").select(
        "complaint_id, tracking_token, status, category, created_at"
    ).order("created_at", desc=True).limit(10).execute()
    return result.data


@router.get("/test/token")
async def test_token():
    from app.services.token_generator import generate_tracking_token
    from app.services.sla_service import calculate_sla
    from app.services.geo_mapper import get_ward_from_coordinates, get_zone_room

    ward = get_ward_from_coordinates(19.12, 72.85)
    token = generate_tracking_token("Water Supply", ward)
    sla = calculate_sla("Water Supply", "HIGH")
    zone = get_zone_room(ward)
    return {"token": token, "ward": ward, "zone": zone, "sla_days": sla}

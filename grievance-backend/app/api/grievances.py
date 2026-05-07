from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from datetime import datetime

from app.services.routing_engine import run_routing_engine


router = APIRouter(prefix="/grievances", tags=["grievances"])


@router.post("/")
async def submit_grievance(
    title: str = Form(...),
    description: str = Form(...),
    channel: str = Form("web"),
    lat: float = Form(...),
    lng: float = Form(...),
    citizen_name: str = Form(...),
    citizen_phone: str = Form(...),
    file: UploadFile | None = File(None),
    background_tasks: BackgroundTasks = None,
):
    """Submit a citizen grievance and route it through the processing pipeline."""
    try:
        # Save grievance to MongoDB
        from app.db.mongo import grievances_collection
        
        grievance_doc = {
            "title": title,
            "description": description,
            "channel": channel,
            "citizen_name": citizen_name,
            "citizen_phone": citizen_phone,
            "lat": lat,
            "lng": lng,
            "file_name": file.filename if file else None,
            "status": "submitted",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        
        result = await grievances_collection.insert_one(grievance_doc)
        grievance_id = str(result.inserted_id)
    except Exception as e:
        # Fallback if MongoDB unavailable
        print(f"Warning: Failed to save to MongoDB: {str(e)}")
        grievance_id = "temp-grievance-id"
    
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
    }

from fastapi import APIRouter, UploadFile, File, Form
from datetime import datetime

router = APIRouter(prefix="/grievances", tags=["grievances"])


@router.post("/")
async def submit_grievance(
    title: str = Form(...),
    description: str = Form(...),
    channel: str = Form("web"),
    file: UploadFile | None = File(None),
):
    """Temporary grievance submission endpoint (no DB persistence yet)."""
    created_at = datetime.utcnow().isoformat() + "Z"

    return {
        "message": "Grievance submission endpoint ready",
        "data": {
            "title": title,
            "description": description,
            "channel": channel,
            "status": "pending",
            "created_at": created_at,
            "file_name": file.filename if file else None,
        },
        "note": "Database persistence will be integrated later",
    }

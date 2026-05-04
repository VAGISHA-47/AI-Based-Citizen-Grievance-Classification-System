from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from datetime import datetime

from app.services.ai_pipeline import run_ai_pipeline


router = APIRouter(prefix="/grievances", tags=["grievances"])


@router.post("/")
async def submit_grievance(
    title: str = Form(...),
    description: str = Form(...),
    channel: str = Form("web"),
    file: UploadFile | None = File(None),
    background_tasks: BackgroundTasks = None,
):
    """Temporary grievance submission endpoint (queues AI placeholder, no DB persistence yet)."""
    created_at = datetime.utcnow().isoformat() + "Z"

    # Create a temporary mock grievance id so frontend and DB teammate have a contract
    mock_grievance_id = "temp-grievance-id"

    # Queue the AI pipeline as a background task (AI teammate will provide real implementation)
    if background_tasks is not None:
        background_tasks.add_task(
            run_ai_pipeline,
            mock_grievance_id,
            f"{title}\n{description}",
        )

    return {
        "message": "Grievance submitted successfully",
        "id": mock_grievance_id,
        "status": "processing",
        "ai_status": "queued",
        "data": {
            "title": title,
            "description": description,
            "channel": channel,
            "file_name": file.filename if file else None,
        },
        "note": "Database and AI/ML integrations will be added later by teammates",
    }

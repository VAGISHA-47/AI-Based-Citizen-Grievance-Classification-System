from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/officer", tags=["officer"])


class ResolveGrievanceRequest(BaseModel):
    feedback: str


class UpdateStatusRequest(BaseModel):
    status: str
    comment: str | None = None


@router.get("/assigned")
async def get_assigned_grievances():
    """Return mock assigned grievances for the officer dashboard."""
    return {
        "message": "Assigned grievances endpoint ready",
        "officer_id": "mock-officer-id",
        "grievances": [],
        "note": "Database query will be integrated later",
    }


@router.patch("/{grievance_id}/resolve")
async def resolve_grievance(grievance_id: str, request: ResolveGrievanceRequest):
    """Mock grievance resolution endpoint; DB update integrated later."""
    resolved_at = datetime.utcnow().isoformat() + "Z"
    return {
        "message": "Grievance resolution endpoint ready",
        "grievance_id": grievance_id,
        "status": "resolved",
        "feedback": request.feedback,
        "resolved_at": resolved_at,
        "note": "Database update will be integrated later",
    }


@router.patch("/{grievance_id}/status")
async def update_status(grievance_id: str, request: UpdateStatusRequest):
    """Mock status update endpoint for officer to change grievance status."""
    updated_at = datetime.utcnow().isoformat() + "Z"
    return {
        "message": "Grievance status update endpoint ready",
        "grievance_id": grievance_id,
        "status": request.status,
        "comment": request.comment,
        "updated_at": updated_at,
        "note": "Database update will be integrated later",
    }


@router.get("/analytics/summary")
async def analytics_summary():
    """Mock analytics summary for officer dashboard."""
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

from fastapi import APIRouter

from app.services.officer_service import build_officer_queue_response, build_officer_summary_response


router = APIRouter(prefix="/api/v1/officers", tags=["officer-v1"])


@router.get("/me/queue")
async def get_my_queue():
    return build_officer_queue_response()


@router.get("/analytics/summary")
async def analytics_summary():
    return build_officer_summary_response()
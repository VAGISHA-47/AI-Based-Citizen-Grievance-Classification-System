from fastapi import APIRouter, Query

from app.services.supabase_service import list_areas, list_districts, list_states, list_wards


router = APIRouter(prefix="/api/v1/locations", tags=["locations-v1"])


@router.get("/states")
async def get_states():
    return list_states()


@router.get("/districts")
async def get_districts(state_id: int = Query(..., ge=1)):
    return list_districts(state_id)


@router.get("/areas")
async def get_areas(district_id: int = Query(..., ge=1)):
    return list_areas(district_id)


@router.get("/wards")
async def get_wards(area_id: int = Query(..., ge=1)):
    return list_wards(area_id)

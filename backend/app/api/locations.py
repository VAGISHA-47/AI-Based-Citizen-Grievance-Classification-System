from fastapi import APIRouter
from app.db.supabase_client import supabase

router = APIRouter(prefix="/api/v1/locations", tags=["locations"])


@router.get("/states")
def get_states():
    """Get all states from locations."""
    result = supabase.table("states").select("state_id, state_name, state_code").execute()
    return result.data


@router.get("/districts")
def get_districts(state_id: int):
    """Get all districts from locations."""
    result = supabase.table("districts").select("district_id, district_name").eq("state_id", state_id).execute()
    return result.data


@router.get("/areas")
def get_areas(district_id: int):
    """Get all areas from locations."""
    result = supabase.table("areas").select("area_id, area_name, pincode").eq("district_id", district_id).execute()
    return result.data


@router.get("/wards")
def get_wards(area_id: int):
    """Get all wards from locations."""
    result = supabase.table("wards").select("ward_id, ward_number, ward_name").eq("area_id", area_id).execute()
    return result.data

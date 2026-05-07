from fastapi import APIRouter


router = APIRouter(prefix="/api/v1/authority", tags=["authority-v1"])


@router.get("/health")
async def authority_health_check():
    return {"message": "Authority dashboard API is running"}
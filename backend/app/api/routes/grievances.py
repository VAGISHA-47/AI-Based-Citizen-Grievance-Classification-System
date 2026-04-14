from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.grievance import GrievanceStatus
from app.models.user import User, UserRole
from app.schemas.grievance import GrievanceCreate, GrievanceOut, GrievanceStatusUpdate, PredictionOut
from app.services.grievance_service import (
    get_grievance_or_404,
    list_grievances,
    submit_grievance,
    update_grievance_status,
)


router = APIRouter(prefix="/grievances", tags=["grievances"])


@router.post("/submit", response_model=GrievanceOut, status_code=status.HTTP_201_CREATED)
def submit(
    payload: GrievanceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    grievance, _ = submit_grievance(db, user, payload.title, payload.description)
    return grievance


@router.get("/", response_model=list[GrievanceOut])
def list_all(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return list_grievances(db, user)


@router.get("/{grievance_id}", response_model=GrievanceOut)
def track(grievance_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    grievance = get_grievance_or_404(db, grievance_id)
    if user.role == UserRole.citizen and grievance.submitted_by_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    return grievance


@router.patch("/{grievance_id}/status", response_model=GrievanceOut)
def update_status(
    grievance_id: int,
    payload: GrievanceStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role not in {UserRole.officer, UserRole.admin}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Officer/Admin role required")

    grievance = get_grievance_or_404(db, grievance_id)
    return update_grievance_status(db, grievance, payload.status)


@router.get("/{grievance_id}/prediction", response_model=PredictionOut)
def prediction_details(
    grievance_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    grievance = get_grievance_or_404(db, grievance_id)
    if user.role == UserRole.citizen and grievance.submitted_by_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    return PredictionOut(
        category=grievance.category,
        confidence=grievance.similarity_score or 0.0,
        priority=grievance.priority,
        is_duplicate=bool(grievance.duplicate_of_id),
        duplicate_of_id=grievance.duplicate_of_id,
        similarity_score=grievance.similarity_score,
    )

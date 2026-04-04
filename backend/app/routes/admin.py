from collections import defaultdict
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Complaint, User
from app.schemas import ComplaintResponse, DashboardStats

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    _: User = Depends(_require_admin),
):
    complaints = db.query(Complaint).all()

    by_category: dict = defaultdict(int)
    by_priority: dict = defaultdict(int)
    by_status: dict = defaultdict(int)
    by_department: dict = defaultdict(int)

    for c in complaints:
        by_category[c.category or "unknown"] += 1
        by_priority[c.priority or "normal"] += 1
        by_status[c.status or "pending"] += 1
        by_department[c.department or "unknown"] += 1

    return DashboardStats(
        total=len(complaints),
        by_category=dict(by_category),
        by_priority=dict(by_priority),
        by_status=dict(by_status),
        by_department=dict(by_department),
    )


@router.get("/complaints", response_model=List[ComplaintResponse])
def get_all_complaints(
    db: Session = Depends(get_db),
    _: User = Depends(_require_admin),
):
    return db.query(Complaint).order_by(Complaint.created_at.desc()).all()

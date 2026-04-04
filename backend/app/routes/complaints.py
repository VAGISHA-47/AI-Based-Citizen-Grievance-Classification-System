import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, get_optional_user
from app.database import get_db
from app.ml.classifier import GrievanceClassifier
from app.ml.preprocessor import GrievancePreprocessor
from app.models import Complaint, User
from app.schemas import ComplaintCreate, ComplaintResponse, ComplaintUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/complaints", tags=["complaints"])

_classifier = GrievanceClassifier()
_preprocessor = GrievancePreprocessor()


@router.post("/", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def submit_complaint(
    complaint_in: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    # Language detection & optional translation
    full_text = f"{complaint_in.title} {complaint_in.description}"
    lang = _preprocessor.detect_language(full_text)
    translated = None
    text_for_classification = full_text
    if lang != "en":
        translated = _preprocessor.translate_to_english(full_text, lang)
        text_for_classification = translated

    # Classification
    try:
        result = _classifier.classify(text_for_classification)
    except Exception as exc:
        logger.error("Classification error: %s", exc)
        result = {
            "category": "public_services",
            "department": "Public Services Department",
            "priority": "normal",
            "confidence_score": 0.0,
            "sentiment_score": 0.0,
        }

    complaint = Complaint(
        user_id=current_user.id if current_user else None,
        title=complaint_in.title,
        description=complaint_in.description,
        original_language=lang,
        translated_text=translated,
        category=result["category"],
        department=result["department"],
        priority=result["priority"],
        sentiment_score=result["sentiment_score"],
        confidence_score=result["confidence_score"],
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("/", response_model=List[ComplaintResponse])
def list_complaints(
    category: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    complaint_status: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    query = db.query(Complaint)

    # Citizens only see their own complaints; admins/officers see all
    if current_user and current_user.role == "citizen":
        query = query.filter(Complaint.user_id == current_user.id)

    if category:
        query = query.filter(Complaint.category == category)
    if department:
        query = query.filter(Complaint.department == department)
    if priority:
        query = query.filter(Complaint.priority == priority)
    if complaint_status:
        query = query.filter(Complaint.status == complaint_status)

    return query.order_by(Complaint.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Citizens can only view their own complaints
    if current_user and current_user.role == "citizen":
        if complaint.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

    return complaint


@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
def update_complaint_status(
    complaint_id: int,
    update: ComplaintUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in ("admin", "department_officer"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if update.status is not None:
        complaint.status = update.status
    if update.priority is not None:
        complaint.priority = update.priority

    db.commit()
    db.refresh(complaint)
    return complaint


@router.delete("/{complaint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    db.delete(complaint)
    db.commit()

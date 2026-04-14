from sqlalchemy.orm import Session

from app.ml.classifier import ClassificationResult, classifier
from app.models.grievance import Grievance, GrievanceStatus
from app.models.user import User, UserRole


def submit_grievance(db: Session, user: User, title: str, description: str) -> tuple[Grievance, ClassificationResult]:
    existing = db.query(Grievance.id, Grievance.description).all()
    existing_map = {item.id: item.description for item in existing}

    text = f"{title}. {description}"
    prediction = classifier.classify(text, existing_map)

    grievance = Grievance(
        title=title,
        description=description,
        category=prediction.category,
        priority=prediction.priority,
        duplicate_of_id=prediction.duplicate_of_id,
        similarity_score=prediction.similarity_score,
        submitted_by_id=user.id,
        status=GrievanceStatus.submitted,
    )

    db.add(grievance)
    db.commit()
    db.refresh(grievance)
    return grievance, prediction


def list_grievances(db: Session, user: User) -> list[Grievance]:
    query = db.query(Grievance).order_by(Grievance.created_at.desc())
    if user.role in {UserRole.officer, UserRole.admin}:
        return query.all()
    return query.filter(Grievance.submitted_by_id == user.id).all()


def get_grievance_or_404(db: Session, grievance_id: int) -> Grievance:
    grievance = db.query(Grievance).filter(Grievance.id == grievance_id).first()
    if not grievance:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grievance not found")
    return grievance


def update_grievance_status(db: Session, grievance: Grievance, status_value: GrievanceStatus) -> Grievance:
    grievance.status = status_value
    db.add(grievance)
    db.commit()
    db.refresh(grievance)
    return grievance

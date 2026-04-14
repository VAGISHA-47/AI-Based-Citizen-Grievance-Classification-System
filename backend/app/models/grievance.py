import enum

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class GrievanceStatus(str, enum.Enum):
    submitted = "submitted"
    in_review = "in_review"
    resolved = "resolved"


class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(220), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(120), nullable=False, default="Other")
    priority = Column(String(40), nullable=False, default="medium")
    status = Column(Enum(GrievanceStatus), nullable=False, default=GrievanceStatus.submitted)

    duplicate_of_id = Column(Integer, ForeignKey("grievances.id"), nullable=True)
    similarity_score = Column(Float, nullable=True)

    submitted_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    submitted_by = relationship("User", back_populates="grievances")
    duplicate_of = relationship("Grievance", remote_side=[id], uselist=False)

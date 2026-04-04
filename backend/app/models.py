from datetime import datetime

from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String(20), default="citizen")
    created_at = Column(DateTime, default=lambda: datetime.utcnow())

    complaints = relationship("Complaint", back_populates="user")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    original_language = Column(String(10), default="en")
    translated_text = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    department = Column(String(100), nullable=True)
    priority = Column(String(20), default="normal")
    sentiment_score = Column(Float, nullable=True)
    status = Column(String(20), default="pending")
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow())

    user = relationship("User", back_populates="complaints")

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, EmailStr


# ── User schemas ──────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Auth schemas ──────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str


# ── Complaint schemas ─────────────────────────────────────────────────────────

class ComplaintCreate(BaseModel):
    title: str
    description: str


class ComplaintResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    title: str
    description: str
    original_language: Optional[str] = None
    translated_text: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    priority: Optional[str] = None
    sentiment_score: Optional[float] = None
    status: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None


# ── ML / classification schemas ───────────────────────────────────────────────

class ClassificationResult(BaseModel):
    category: str
    department: str
    priority: str
    confidence_score: float
    sentiment_score: float


# ── Dashboard schemas ─────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    total: int
    by_category: Dict[str, int]
    by_priority: Dict[str, int]
    by_status: Dict[str, int]
    by_department: Dict[str, int]

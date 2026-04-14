from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.grievance import GrievanceStatus


class GrievanceCreate(BaseModel):
    title: str = Field(min_length=4, max_length=220)
    description: str = Field(min_length=10)


class GrievanceStatusUpdate(BaseModel):
    status: GrievanceStatus


class GrievanceOut(BaseModel):
    id: int
    title: str
    description: str
    category: str
    priority: str
    status: GrievanceStatus
    duplicate_of_id: int | None
    similarity_score: float | None
    submitted_by_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PredictionOut(BaseModel):
    category: str
    confidence: float
    priority: str
    is_duplicate: bool
    duplicate_of_id: int | None
    similarity_score: float | None

"""
Pydantic schemas for request and response payloads.

These schemas define the shapes of data exchanged via the API.
Database models (SQLAlchemy) are implemented by another teammate; these
schemas remain independent and are safe to use now for validation and
to-be-returned responses.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None


class GrievanceCreate(BaseModel):
    title: str
    description: str
    channel: str


class GrievanceResponse(BaseModel):
    id: str
    title: str
    description: str
    channel: str
    status: str

"""
Authentication utilities: JWT token creation/verification and password hashing.

These helpers are intentionally database-agnostic so the database teammate
can integrate models and persistence later.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings


# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: Dict) -> str:
    """Create a JWT access token with expiry from settings."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    secret_key = settings.JWT_SECRET or settings.SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
    """Decode and verify a JWT token. Return the payload or None if invalid."""
    try:
        secret_key = settings.JWT_SECRET or settings.SECRET_KEY
        payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

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
    from datetime import timezone
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    # Safely get JWT_SECRET with fallback to SECRET_KEY
    secret_key = getattr(settings, "JWT_SECRET", None) or getattr(settings, "SECRET_KEY", None)
    if not secret_key:
        raise ValueError("JWT_SECRET or SECRET_KEY must be configured in environment variables")
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
    """Decode and verify a JWT token. Return the payload or None if invalid."""
    try:
        # Safely get JWT_SECRET with fallback to SECRET_KEY
        secret_key = getattr(settings, "JWT_SECRET", None) or getattr(settings, "SECRET_KEY", None)
        if not secret_key:
            return None
        
        payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

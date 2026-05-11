"""
Authentication utilities: JWT token creation/verification and password hashing.

These helpers are intentionally database-agnostic so the database teammate
can integrate models and persistence later.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict

from jose import jwt, JWTError
import bcrypt

from app.config import settings


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
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")

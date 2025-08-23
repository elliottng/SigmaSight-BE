"""
Authentication utilities for SigmaSight Backend
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.core.logging import auth_logger

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        auth_logger.error(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)  # Default 24 hours
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        auth_logger.info(f"JWT token created for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        auth_logger.error(f"JWT token creation error: {e}")
        raise


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            auth_logger.warning("JWT token missing 'sub' claim")
            return None
            
        return payload
    except JWTError as e:
        auth_logger.warning(f"JWT token verification failed: {e}")
        return None
    except Exception as e:
        auth_logger.error(f"JWT token verification error: {e}")
        return None


def create_token_response(user_id: str, email: str) -> Dict[str, Any]:
    """Create a token response for a user"""
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={"sub": str(user_id), "email": email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 24 * 3600,  # 24 hours in seconds
        "user_id": str(user_id),
        "email": email
    }

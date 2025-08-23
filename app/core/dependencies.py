"""
FastAPI dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional

from app.core.auth import verify_token
from app.database import get_db
from app.models.users import User
from app.schemas.auth import CurrentUser
from app.core.logging import auth_logger

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> CurrentUser:
    """
    Dependency to get the current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify and decode the JWT token
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        
        # Convert string to UUID
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            auth_logger.warning(f"Invalid UUID format in token: {user_id_str}")
            raise credentials_exception
        
    except Exception as e:
        auth_logger.error(f"Token validation error: {e}")
        raise credentials_exception
    
    # Get user from database
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            auth_logger.warning(f"User not found in database: {user_id}")
            raise credentials_exception
        
        if not user.is_active:
            auth_logger.warning(f"Inactive user attempted access: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
        
        # Return CurrentUser schema
        return CurrentUser.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"Database error during user lookup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


async def get_current_active_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Dependency to get the current active user (redundant check but explicit)
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# Optional user dependency (doesn't raise if no token)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[CurrentUser]:
    """
    Optional dependency that returns None if no valid token is provided
    """
    if credentials is None:
        return None
    
    try:
        # Reuse the existing logic but catch exceptions
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
    except Exception:
        return None


async def require_admin(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Dependency that requires admin privileges.
    For now, just requires authenticated user - can be enhanced later.
    """
    # TODO: Add proper admin role check
    # For demo stage, any authenticated user can access admin endpoints
    return current_user

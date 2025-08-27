"""
FastAPI dependencies for authentication and authorization
"""
from fastapi import Cookie, Depends, HTTPException, Request, status
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

# HTTP Bearer token security scheme (with auto_error=False for dual auth)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_cookie: Optional[str] = Cookie(None, alias="auth_token"),
    db: AsyncSession = Depends(get_db)
) -> CurrentUser:
    """
    Dependency to get the current authenticated user.
    Supports dual authentication: Bearer token (preferred) or Cookie (fallback).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try Bearer token first (preferred for regular API calls)
    token = None
    auth_method = None
    
    if credentials and credentials.credentials:
        token = credentials.credentials
        auth_method = "bearer"
        auth_logger.debug("Using Bearer token authentication")
    # Fall back to cookie (needed for SSE)
    elif auth_cookie:
        token = auth_cookie
        auth_method = "cookie"
        auth_logger.debug("Using cookie authentication")
    else:
        auth_logger.warning("No valid authentication provided (neither Bearer nor cookie)")
        raise credentials_exception
    
    try:
        # Verify and decode the JWT token (same logic regardless of source)
        payload = verify_token(token)
        if payload is None:
            auth_logger.warning(f"Token verification failed (auth method: {auth_method})")
            raise credentials_exception
        
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            auth_logger.warning(f"No subject in token (auth method: {auth_method})")
            raise credentials_exception
        
        # Convert string to UUID
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            auth_logger.warning(f"Invalid UUID format in token: {user_id_str} (auth method: {auth_method})")
            raise credentials_exception
        
    except HTTPException:
        raise
    except Exception as e:
        auth_logger.error(f"Token validation error: {e} (auth method: {auth_method})")
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
        
        # Log successful authentication with method used
        auth_logger.info(f"User authenticated successfully: {user.email} (method: {auth_method})")
        
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
    auth_cookie: Optional[str] = Cookie(None, alias="auth_token"),
    db: AsyncSession = Depends(get_db)
) -> Optional[CurrentUser]:
    """
    Optional dependency that returns None if no valid token is provided.
    Supports both Bearer token and cookie authentication.
    """
    if not credentials and not auth_cookie:
        return None
    
    try:
        # Reuse the existing dual-auth logic but catch exceptions
        return await get_current_user(credentials, auth_cookie, db)
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

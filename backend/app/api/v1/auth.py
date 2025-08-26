"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4

from app.database import get_db
from app.core.auth import verify_password, get_password_hash, create_token_response
from app.core.dependencies import get_current_user
from app.models.users import User, Portfolio
from app.schemas.auth import UserLogin, UserRegister, TokenResponse, UserResponse, CurrentUser
from app.core.logging import auth_logger

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login")
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token"""
    auth_logger.info(f"Login attempt for email: {user_login.email}")
    
    # Get user by email
    stmt = select(User).where(User.email == user_login.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        auth_logger.warning(f"Login failed - user not found: {user_login.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        auth_logger.warning(f"Login failed - inactive user: {user_login.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account"
        )
    
    if not verify_password(user_login.password, user.hashed_password):
        auth_logger.warning(f"Login failed - incorrect password: {user_login.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create and return JWT token
    token_data = create_token_response(str(user.id), user.email)
    auth_logger.info(f"Login successful for user: {user.email}")
    
    # Return simple token response (not TokenResponse schema which expects user field)
    return {
        "access_token": token_data["access_token"],
        "token_type": token_data["token_type"],
        "expires_in": token_data["expires_in"]
    }


@router.post("/register", response_model=UserResponse)
async def register(user_register: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user (admin-only initially)"""
    auth_logger.info(f"Registration attempt for email: {user_register.email}")
    
    # Check if user already exists
    stmt = select(User).where(User.email == user_register.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        auth_logger.warning(f"Registration failed - email already exists: {user_register.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_register.password)
    new_user = User(
        id=uuid4(),
        email=user_register.email,
        full_name=user_register.full_name,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(new_user)
    
    # Create portfolio for the user
    portfolio = Portfolio(
        id=uuid4(),
        user_id=new_user.id,
        name=f"{user_register.full_name}'s Portfolio"
    )
    
    db.add(portfolio)
    
    try:
        await db.commit()
        await db.refresh(new_user)
        auth_logger.info(f"User registered successfully: {user_register.email}")
        return UserResponse.model_validate(new_user)
    except Exception as e:
        await db.rollback()
        auth_logger.error(f"Registration failed for {user_register.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.get("/me", response_model=CurrentUser)
async def get_current_user_info(current_user: CurrentUser = Depends(get_current_user)):
    """Get current authenticated user information"""
    auth_logger.info(f"User info requested: {current_user.email}")
    return current_user


@router.post("/refresh")
async def refresh_token(current_user: CurrentUser = Depends(get_current_user)):
    """Refresh JWT token (for V1, just return a new token)"""
    auth_logger.info(f"Token refresh requested: {current_user.email}")
    
    # For V1, we just create a new token with the same data
    token_data = create_token_response(str(current_user.id), current_user.email)
    
    return {
        "access_token": token_data["access_token"],
        "token_type": token_data["token_type"],
        "expires_in": token_data["expires_in"]
    }


@router.post("/logout")
async def logout(current_user: CurrentUser = Depends(get_current_user)):
    """Logout endpoint - invalidates session (client should discard token)"""
    auth_logger.info(f"Logout requested: {current_user.email}")
    
    # For JWT-based auth, logout is handled client-side by discarding the token
    # In V2, we could add token blacklisting if needed
    return {"message": "Successfully logged out", "success": True}

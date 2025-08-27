"""
Portfolio management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from decimal import Decimal
from typing import List

from app.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import CurrentUser
from app.models.users import Portfolio
from app.models.positions import Position
from app.core.logging import api_logger

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/")
async def get_portfolio(current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get portfolio overview"""
    api_logger.info(f"Portfolio overview requested by user: {current_user.email}")
    
    # Get user's portfolio with positions
    try:
        stmt = select(Portfolio).where(
            Portfolio.user_id == current_user.id
        ).options(selectinload(Portfolio.positions))
        
        result = await db.execute(stmt)
        portfolio = result.scalar_one_or_none()
        
        if not portfolio:
            api_logger.warning(f"No portfolio found for user: {current_user.email}")
            return {
                "portfolios": [],
                "total_portfolios": 0,
                "message": "No portfolios found for user"
            }
        
        # Calculate portfolio metrics
        total_market_value = Decimal('0.00')
        position_count = 0
        positions_data = []
        
        for position in portfolio.positions:
            if position.deleted_at is None:  # Only active positions
                position_count += 1
                if position.market_value:
                    total_market_value += position.market_value
                
                positions_data.append({
                    "id": str(position.id),
                    "symbol": position.symbol,
                    "position_type": position.position_type.value,
                    "quantity": float(position.quantity),
                    "entry_price": float(position.entry_price),
                    "market_value": float(position.market_value) if position.market_value else None,
                    "unrealized_pnl": float(position.unrealized_pnl) if position.unrealized_pnl else None
                })
        
        portfolio_data = {
            "id": str(portfolio.id),
            "name": portfolio.name,
            "description": portfolio.description,
            "currency": portfolio.currency,
            "total_market_value": float(total_market_value),
            "position_count": position_count,
            "positions": positions_data,
            "created_at": portfolio.created_at.isoformat(),
            "updated_at": portfolio.updated_at.isoformat()
        }
        
        api_logger.info(f"Portfolio overview returned for user {current_user.email}: {position_count} positions, ${total_market_value} total value")
        
        return {
            "portfolios": [portfolio_data],
            "total_portfolios": 1,
            "user_id": str(current_user.id),
            "email": current_user.email
        }
        
    except Exception as e:
        api_logger.error(f"Error retrieving portfolio for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving portfolio"
        )


@router.post("/upload")
async def upload_portfolio(current_user: CurrentUser = Depends(get_current_user)):
    """Upload portfolio CSV"""
    api_logger.info(f"Portfolio upload requested by user: {current_user.email}")
    # TODO: Implement CSV upload and processing
    return {
        "message": "Portfolio upload endpoint - TODO",
        "user_id": str(current_user.id)
    }


@router.get("/summary")
async def get_portfolio_summary(current_user: CurrentUser = Depends(get_current_user)):
    """Get portfolio summary statistics"""
    api_logger.info(f"Portfolio summary requested by user: {current_user.email}")
    # TODO: Implement portfolio summary
    return {
        "message": "Portfolio summary endpoint - TODO",
        "user_id": str(current_user.id)
    }

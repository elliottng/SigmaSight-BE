"""
Daily batch calculations for portfolio analytics
Integrates Section 1.4.1 market data calculations with batch processing
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.core.logging import get_logger
from app.models.positions import Position
from app.models.users import Portfolio
from app.calculations.market_data import (
    bulk_update_position_values,
    fetch_and_cache_prices
)

logger = get_logger(__name__)


async def run_daily_calculations():
    """
    Run daily portfolio calculations using Section 1.4.1 functions
    This implements the batch processing framework outlined in TODO Section 1.6
    
    Sequence:
    1. Update market data cache (via market_data_sync.py - already implemented)
    2. Calculate position market values and daily P&L
    3. Update portfolio aggregations
    4. Calculate risk metrics (future sections)
    5. Generate portfolio snapshots (future sections)
    """
    start_time = datetime.now()
    logger.info(f"Starting daily calculations at {start_time}")
    
    try:
        async with async_session_maker() as db:
            # Step 1: Update all position market values and daily P&L
            position_update_results = await update_all_position_values(db)
            
            # Step 2: Calculate portfolio aggregations
            portfolio_results = await calculate_portfolio_aggregations(db)
            
            # Future: Step 3 would be Greeks calculations (Section 1.4.2)
            # Future: Step 4 would be risk metrics (Section 1.4.5)
            # Future: Step 5 would be portfolio snapshots (Section 1.4.6)
            
            duration = datetime.now() - start_time
            logger.info(f"Daily calculations completed in {duration.total_seconds():.2f}s")
            
            return {
                "duration_seconds": duration.total_seconds(),
                "position_updates": position_update_results,
                "portfolio_aggregations": portfolio_results,
                "success": True
            }
            
    except Exception as e:
        logger.error(f"Daily calculations failed: {str(e)}")
        raise


async def update_all_position_values(db: AsyncSession) -> Dict[str, Any]:
    """
    Update market values and daily P&L for all active positions
    Uses Section 1.4.1 calculation functions
    """
    logger.info("Starting position value updates...")
    
    # Get all active positions (not soft-deleted, not exited)
    stmt = select(Position).where(
        Position.deleted_at.is_(None),
        Position.exit_date.is_(None)
    )
    result = await db.execute(stmt)
    active_positions = result.scalars().all()
    
    if not active_positions:
        logger.info("No active positions found")
        return {"positions_processed": 0, "success": True}
    
    logger.info(f"Found {len(active_positions)} active positions to update")
    
    # Use bulk update function from Section 1.4.1
    update_results = await bulk_update_position_values(db, active_positions)
    
    # Analyze results
    successful_updates = [r for r in update_results if r.get('success')]
    failed_updates = [r for r in update_results if not r.get('success')]
    
    logger.info(f"Position updates complete: {len(successful_updates)} successful, {len(failed_updates)} failed")
    
    if failed_updates:
        failed_symbols = [r.get('symbol', 'unknown') for r in failed_updates]
        logger.warning(f"Failed to update positions for symbols: {failed_symbols}")
    
    return {
        "positions_processed": len(active_positions),
        "successful_updates": len(successful_updates),
        "failed_updates": len(failed_updates),
        "failed_symbols": [r.get('symbol') for r in failed_updates],
        "success": len(failed_updates) == 0
    }


async def calculate_portfolio_aggregations(db: AsyncSession) -> Dict[str, Any]:
    """
    Calculate portfolio-level aggregations from updated position values
    Implements portfolio aggregation logic from legacy system
    """
    logger.info("Starting portfolio aggregations...")
    
    # Get all portfolios
    stmt = select(Portfolio).where(Portfolio.deleted_at.is_(None))
    result = await db.execute(stmt)
    portfolios = result.scalars().all()
    
    aggregation_results = []
    
    for portfolio in portfolios:
        try:
            # Get portfolio's active positions with updated values
            stmt = select(Position).where(
                Position.portfolio_id == portfolio.id,
                Position.deleted_at.is_(None),
                Position.exit_date.is_(None)
            )
            result = await db.execute(stmt)
            positions = result.scalars().all()
            
            if not positions:
                logger.info(f"Portfolio {portfolio.id} has no active positions")
                continue
            
            # Calculate portfolio aggregations
            portfolio_agg = await calculate_single_portfolio_aggregation(portfolio, positions)
            aggregation_results.append(portfolio_agg)
            
            logger.debug(f"Portfolio {portfolio.id} aggregation: {portfolio_agg}")
            
        except Exception as e:
            logger.error(f"Error calculating aggregations for portfolio {portfolio.id}: {str(e)}")
            aggregation_results.append({
                "portfolio_id": portfolio.id,
                "success": False,
                "error": str(e)
            })
    
    successful_aggs = [r for r in aggregation_results if r.get('success')]
    failed_aggs = [r for r in aggregation_results if not r.get('success')]
    
    logger.info(f"Portfolio aggregations complete: {len(successful_aggs)} successful, {len(failed_aggs)} failed")
    
    return {
        "portfolios_processed": len(portfolios),
        "successful_aggregations": len(successful_aggs),
        "failed_aggregations": len(failed_aggs),
        "aggregation_results": aggregation_results,
        "success": len(failed_aggs) == 0
    }


async def calculate_single_portfolio_aggregation(
    portfolio: Portfolio, 
    positions: List[Position]
) -> Dict[str, Any]:
    """
    Calculate aggregated metrics for a single portfolio
    Based on legacy portfolio aggregation logic from get_data.py
    """
    from decimal import Decimal
    
    # Initialize aggregations
    total_market_value = Decimal('0')
    total_exposure = Decimal('0')
    long_value = Decimal('0')
    short_value = Decimal('0')
    daily_pnl = Decimal('0')
    num_positions = len(positions)
    num_long = 0
    num_short = 0
    
    for position in positions:
        # Market value (always positive)
        if position.market_value:
            total_market_value += position.market_value
        
        # Exposure (signed based on quantity)
        if position.market_value and position.quantity:
            exposure = position.market_value if position.quantity > 0 else -position.market_value
            total_exposure += exposure
            
            if position.quantity > 0:
                long_value += position.market_value
                num_long += 1
            else:
                short_value += position.market_value
                num_short += 1
        
        # TODO: Add daily P&L when position.daily_pnl field is available
        # For now, we'll calculate it from unrealized_pnl changes
    
    # Calculate derived metrics
    gross_exposure = long_value + short_value
    net_exposure = long_value - short_value
    
    return {
        "portfolio_id": portfolio.id,
        "total_market_value": total_market_value,
        "total_exposure": total_exposure,
        "gross_exposure": gross_exposure,
        "net_exposure": net_exposure,
        "long_value": long_value,
        "short_value": short_value,
        "num_positions": num_positions,
        "num_long_positions": num_long,
        "num_short_positions": num_short,
        "calculation_timestamp": datetime.utcnow(),
        "success": True
    }


async def get_portfolio_symbols(db: AsyncSession, portfolio_id: str) -> List[str]:
    """
    Get unique symbols for a portfolio's active positions
    Helper function for targeted price fetching
    """
    stmt = select(Position.symbol).where(
        Position.portfolio_id == portfolio_id,
        Position.deleted_at.is_(None),
        Position.exit_date.is_(None)
    ).distinct()
    
    result = await db.execute(stmt)
    symbols = result.scalars().all()
    
    return list(symbols)


# Legacy function stubs - these will be implemented in future sections
async def calculate_factor_exposures():
    """Calculate factor exposures for all portfolios - Section 1.4.4"""
    logger.info("Factor exposures calculation - TODO Section 1.4.4")
    pass

async def calculate_risk_metrics():
    """Calculate risk metrics for all portfolios - Section 1.4.5"""
    logger.info("Risk metrics calculation - TODO Section 1.4.5")
    pass

async def update_options_greeks():
    """Update Greeks for all options positions - Section 1.4.2"""
    logger.info("Options Greeks calculation - TODO Section 1.4.2")
    pass


if __name__ == "__main__":
    asyncio.run(run_daily_calculations())

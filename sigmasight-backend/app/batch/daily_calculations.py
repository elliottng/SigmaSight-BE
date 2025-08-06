"""
Daily batch calculations for portfolio analytics
NOW USES THE NEW BATCH ORCHESTRATOR - Section 1.6 Implementation Complete
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
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
from app.batch.batch_orchestrator import batch_orchestrator

logger = get_logger(__name__)


async def run_daily_calculations(portfolio_id: Optional[str] = None):
    """
    Run daily portfolio calculations using the new batch orchestrator.
    This now integrates all 8 completed calculation engines from Section 1.6.
    
    Integrated Engines:
    1. Market Data Update (shared across portfolios)
    2. Advanced Portfolio Aggregation (20+ metrics)
    3. Greeks Calculations (for options)
    4. Factor Analysis (with delta adjustment)
    5. Market Risk Scenarios
    6. Stress Testing (18 scenarios)
    7. Correlations (weekly, Tuesday only)
    8. Portfolio Snapshots (comprehensive)
    
    Args:
        portfolio_id: Optional specific portfolio to process
        
    Returns:
        List of job results with status and timing information
    """
    start_time = datetime.now()
    logger.info(f"Starting daily calculations using new orchestrator at {start_time}")
    
    try:
        # Use the new batch orchestrator
        results = await batch_orchestrator.run_daily_batch_sequence(portfolio_id)
        
        duration = datetime.now() - start_time
        
        # Count successes and failures
        successful = sum(1 for r in results if r['status'] == 'completed')
        failed = sum(1 for r in results if r['status'] == 'failed')
        
        logger.info(
            f"Daily calculations completed in {duration.total_seconds():.2f}s: "
            f"{successful} successful, {failed} failed"
        )
        
        return {
            "duration_seconds": duration.total_seconds(),
            "jobs_run": len(results),
            "successful": successful,
            "failed": failed,
            "results": results,
            "success": failed == 0
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

"""
Market data synchronization batch job
"""
import asyncio
from datetime import datetime, date, timedelta
from typing import List, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct

from app.database import AsyncSessionLocal
from app.services.market_data_service import market_data_service
from app.models.positions import Position
from app.models.market_data import MarketDataCache
from app.core.logging import get_logger

logger = get_logger(__name__)


async def sync_market_data():
    """
    Daily market data synchronization from external sources
    - Fetches data for all symbols in active portfolios
    - Updates price data from Polygon.io
    - Updates GICS sector data from YFinance
    """
    start_time = datetime.now()
    logger.info(f"Starting market data sync at {start_time}")
    
    try:
        async with AsyncSessionLocal() as db:
            # Get all unique symbols from active positions
            symbols = await get_active_portfolio_symbols(db)
            
            if not symbols:
                logger.info("No active portfolio symbols found, skipping sync")
                return
            
            logger.info(f"Syncing market data for {len(symbols)} symbols: {', '.join(list(symbols)[:5])}{'...' if len(symbols) > 5 else ''}")
            
            # Fetch and cache market data
            stats = await market_data_service.bulk_fetch_and_cache(
                db=db,
                symbols=list(symbols),
                days_back=5  # Get last 5 trading days for daily sync
            )
            
            duration = datetime.now() - start_time
            logger.info(f"Market data sync completed in {duration.total_seconds():.2f}s: {stats}")
            
            return stats
            
    except Exception as e:
        logger.error(f"Market data sync failed: {str(e)}")
        raise


async def get_active_portfolio_symbols(db: AsyncSession) -> Set[str]:
    """
    Get all unique symbols from active portfolio positions
    
    Args:
        db: Database session
        
    Returns:
        Set of unique symbols
    """
    # Get all unique symbols from positions
    stmt = select(distinct(Position.symbol)).where(Position.quantity != 0)
    result = await db.execute(stmt)
    symbols = result.scalars().all()
    
    # Also include factor ETF symbols for factor calculations
    factor_etfs = ['SPY', 'VTV', 'VUG', 'MTUM', 'QUAL', 'SLY', 'USMV']
    
    all_symbols = set(symbols) | set(factor_etfs)
    
    logger.info(f"Found {len(symbols)} portfolio symbols and {len(factor_etfs)} factor ETFs")
    return all_symbols


async def fetch_missing_historical_data(days_back: int = 90):
    """
    Fetch missing historical data for all portfolio symbols
    
    Args:
        days_back: Number of days to backfill
    """
    logger.info(f"Starting historical data backfill for {days_back} days")
    
    try:
        async with AsyncSessionLocal() as db:
            symbols = await get_active_portfolio_symbols(db)
            
            if not symbols:
                logger.info("No symbols found for historical backfill")
                return
            
            # Check what data we already have
            start_date = date.today() - timedelta(days=days_back)
            
            stmt = select(distinct(MarketDataCache.symbol)).where(
                MarketDataCache.date >= start_date
            )
            result = await db.execute(stmt)
            cached_symbols = set(result.scalars().all())
            
            # Find symbols missing data
            missing_symbols = symbols - cached_symbols
            
            if missing_symbols:
                logger.info(f"Backfilling data for {len(missing_symbols)} symbols")
                stats = await market_data_service.bulk_fetch_and_cache(
                    db=db,
                    symbols=list(missing_symbols),
                    days_back=days_back
                )
                logger.info(f"Historical backfill completed: {stats}")
                return stats
            else:
                logger.info("All symbols already have historical data cached")
                return {"message": "No backfill needed"}
                
    except Exception as e:
        logger.error(f"Historical data backfill failed: {str(e)}")
        raise


async def verify_market_data_quality():
    """
    Verify the quality and completeness of cached market data
    """
    logger.info("Starting market data quality verification")
    
    try:
        async with AsyncSessionLocal() as db:
            # Check for recent data
            recent_date = date.today() - timedelta(days=7)
            
            stmt = select(
                MarketDataCache.symbol,
                MarketDataCache.date
            ).where(
                MarketDataCache.date >= recent_date
            ).order_by(MarketDataCache.symbol, MarketDataCache.date.desc())
            
            result = await db.execute(stmt)
            recent_data = result.all()
            
            # Group by symbol and check latest date
            symbol_latest = {}
            for record in recent_data:
                if record.symbol not in symbol_latest:
                    symbol_latest[record.symbol] = record.date
            
            stale_symbols = []
            for symbol, latest_date in symbol_latest.items():
                days_old = (date.today() - latest_date).days
                if days_old > 3:  # Consider data stale if > 3 days old
                    stale_symbols.append(symbol)
            
            if stale_symbols:
                logger.warning(f"Found {len(stale_symbols)} symbols with stale data: {stale_symbols[:5]}")
            else:
                logger.info("All market data is current")
            
            return {
                "total_symbols": len(symbol_latest),
                "stale_symbols": len(stale_symbols),
                "stale_symbol_list": stale_symbols
            }
            
    except Exception as e:
        logger.error(f"Market data quality verification failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(sync_market_data())

"""
Market Data Calculation Functions - Section 1.4.1
Implements core position valuation and P&L calculations with database integration
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.positions import Position, PositionType
from app.models.market_data import MarketDataCache
from app.services.market_data_service import market_data_service
from app.core.logging import get_logger

logger = get_logger(__name__)


def is_options_position(position: Position) -> bool:
    """
    Determine if a position is an options position
    
    Args:
        position: Position object
        
    Returns:
        True if position is options (LC, LP, SC, SP), False if stock (LONG, SHORT)
    """
    return position.position_type in [
        PositionType.LC,  # Long Call
        PositionType.LP,  # Long Put
        PositionType.SC,  # Short Call
        PositionType.SP   # Short Put
    ]


async def calculate_position_market_value(
    position: Position, 
    current_price: Decimal
) -> Dict[str, Decimal]:
    """
    Calculate current market value and exposure for a position
    Based on legacy logic: market_value = abs(quantity) × price × multiplier
    
    Args:
        position: Position object
        current_price: Current market price (Decimal)
        
    Returns:
        Dictionary with:
        - market_value: Always positive (abs(quantity) × price × multiplier)
        - exposure: Signed value (quantity × price × multiplier) 
        - unrealized_pnl: Current value - cost basis
        - cost_basis: Entry price × quantity × multiplier
        - price_per_share: Current price per share/contract
    """
    logger.debug(f"Calculating market value for {position.symbol} at price ${current_price}")
    
    # Options: 1 contract = 100 shares multiplier
    # Stocks: multiplier = 1
    multiplier = Decimal('100') if is_options_position(position) else Decimal('1')
    
    # Market value is always positive (legacy: abs(quantity) × price)
    market_value = abs(position.quantity) * current_price * multiplier
    
    # Exposure is signed (legacy: quantity × price)
    # Negative for short positions, positive for long positions
    exposure = position.quantity * current_price * multiplier
    
    # Cost basis calculation
    cost_basis = position.quantity * position.entry_price * multiplier
    
    # Unrealized P&L = current exposure - cost basis
    unrealized_pnl = exposure - cost_basis
    
    result = {
        "market_value": market_value,
        "exposure": exposure,
        "unrealized_pnl": unrealized_pnl,
        "cost_basis": cost_basis,
        "price_per_share": current_price,
        "multiplier": multiplier
    }
    
    logger.debug(f"Market value calculation result for {position.symbol}: {result}")
    return result


async def get_previous_trading_day_price(
    db: AsyncSession, 
    symbol: str,
    current_date: Optional[date] = None
) -> Optional[Decimal]:
    """
    Get the most recent price before current_date from market_data_cache
    
    Args:
        db: Database session
        symbol: Symbol to lookup
        current_date: Date to look before (defaults to today)
        
    Returns:
        Previous trading day closing price, or None if not found
    """
    if not current_date:
        current_date = date.today()
    
    logger.debug(f"Looking up previous trading day price for {symbol} before {current_date}")
    
    stmt = select(MarketDataCache.close).where(
        MarketDataCache.symbol == symbol.upper(),
        MarketDataCache.date < current_date
    ).order_by(MarketDataCache.date.desc()).limit(1)
    
    result = await db.execute(stmt)
    price_record = result.scalar_one_or_none()
    
    if price_record:
        logger.debug(f"Found previous price for {symbol}: ${price_record}")
        return price_record
    else:
        logger.warning(f"No previous trading day price found for {symbol}")
        return None


async def calculate_daily_pnl(
    db: AsyncSession,
    position: Position, 
    current_price: Decimal
) -> Dict[str, Decimal]:
    """
    Calculate daily P&L by fetching previous price from database
    Implements database-integrated approach with fallback hierarchy
    
    Args:
        db: Database session
        position: Position object
        current_price: Current price (Decimal)
        
    Returns:
        Dictionary with:
        - daily_pnl: Change in position value
        - daily_return: Percentage change in price
        - price_change: Absolute price change
        - previous_price: Previous trading day price used
        - previous_value: Position value at previous price
        - current_value: Position value at current price
    """
    logger.debug(f"Calculating daily P&L for {position.symbol} at current price ${current_price}")
    
    # Step 1: Try to get previous price from market_data_cache
    previous_price = await get_previous_trading_day_price(db, position.symbol)
    
    # Step 2: Fallback to position.last_price if market data not available
    if previous_price is None:
        previous_price = position.last_price
        if previous_price:
            logger.info(f"Using position.last_price fallback for {position.symbol}: ${previous_price}")
    
    # Step 3: Handle case where no previous price is available
    if previous_price is None:
        logger.warning(f"No previous price available for {position.symbol}, returning zero P&L")
        return {
            "daily_pnl": Decimal('0'),
            "daily_return": Decimal('0'),
            "price_change": Decimal('0'),
            "previous_price": None,
            "previous_value": Decimal('0'),
            "current_value": Decimal('0'),
            "error": "No previous price data available"
        }
    
    # Calculate position values using same multiplier logic
    multiplier = Decimal('100') if is_options_position(position) else Decimal('1')
    
    # Position values (using signed quantity for P&L calculation)
    previous_value = position.quantity * previous_price * multiplier
    current_value = position.quantity * current_price * multiplier
    
    # Daily P&L calculation
    daily_pnl = current_value - previous_value
    
    # Daily return (percentage change in price)
    daily_return = (current_price - previous_price) / previous_price if previous_price > 0 else Decimal('0')
    
    # Price change
    price_change = current_price - previous_price
    
    result = {
        "daily_pnl": daily_pnl,
        "daily_return": daily_return,
        "price_change": price_change,
        "previous_price": previous_price,
        "previous_value": previous_value,
        "current_value": current_value
    }
    
    logger.debug(f"Daily P&L calculation result for {position.symbol}: {result}")
    return result


async def fetch_and_cache_prices(
    db: AsyncSession,
    symbols_list: List[str]
) -> Dict[str, Decimal]:
    """
    Fetch current prices and update market_data_cache
    Integrates with existing MarketDataService with calculation-specific logic
    
    Args:
        db: Database session
        symbols_list: List of unique symbols from positions
        
    Returns:
        Dictionary mapping symbol to current price (Decimal)
        
    Behavior:
        1. Uses MarketDataService.fetch_current_prices() for real-time data
        2. Updates market_data_cache for valid prices  
        3. Falls back to cached prices for symbols with fetch failures
        4. Logs all price retrieval attempts and results
    """
    logger.info(f"Fetching and caching prices for {len(symbols_list)} symbols")
    
    if not symbols_list:
        logger.warning("Empty symbols list provided to fetch_and_cache_prices")
        return {}
    
    # Step 1: Fetch current prices using existing MarketDataService
    try:
        current_prices = await market_data_service.fetch_current_prices(symbols_list)
        logger.info(f"Fetched current prices from API: {len([v for v in current_prices.values() if v is not None])} successful")
    except Exception as e:
        logger.error(f"Error fetching current prices from API: {str(e)}")
        current_prices = {symbol: None for symbol in symbols_list}
    
    # Step 2: Update market_data_cache for symbols with valid prices
    valid_prices = {k: v for k, v in current_prices.items() if v is not None}
    
    if valid_prices:
        try:
            # Update cache with current prices
            await market_data_service.update_market_data_cache(
                db=db,
                symbols=list(valid_prices.keys()),
                start_date=date.today(),
                end_date=date.today(),
                include_gics=False  # Skip GICS for real-time price updates
            )
            logger.info(f"Updated market_data_cache for {len(valid_prices)} symbols")
        except Exception as e:
            logger.error(f"Error updating market_data_cache: {str(e)}")
    
    # Step 3: Fallback to cached prices for symbols with missing data
    missing_symbols = [k for k, v in current_prices.items() if v is None]
    if missing_symbols:
        logger.info(f"Attempting to retrieve cached prices for {len(missing_symbols)} symbols")
        try:
            cached_prices = await market_data_service.get_cached_prices(
                db=db,
                symbols=missing_symbols
            )
            
            # Update current_prices with cached data
            for symbol, cached_price in cached_prices.items():
                if cached_price is not None:
                    current_prices[symbol] = cached_price
                    logger.debug(f"Using cached price for {symbol}: ${cached_price}")
            
        except Exception as e:
            logger.error(f"Error retrieving cached prices: {str(e)}")
    
    # Step 4: Final validation and logging
    final_prices = {k: v for k, v in current_prices.items() if v is not None}
    missing_final = [k for k, v in current_prices.items() if v is None]
    
    logger.info(f"Price fetch complete: {len(final_prices)} prices available, {len(missing_final)} still missing")
    
    if missing_final:
        logger.warning(f"No prices available for symbols: {missing_final}")
    
    return final_prices


async def update_position_market_values(
    db: AsyncSession,
    position: Position,
    current_price: Decimal
) -> Dict[str, Any]:
    """
    Helper function to update a position's market values in the database
    Combines market value and daily P&L calculations and persists to database
    
    Args:
        db: Database session
        position: Position object to update
        current_price: Current market price
        
    Returns:
        Dictionary with all calculated values and update status
    """
    logger.debug(f"Updating market values for position {position.id} ({position.symbol})")
    
    try:
        # Calculate current market value and exposure
        market_value_data = await calculate_position_market_value(position, current_price)
        
        # Calculate daily P&L
        daily_pnl_data = await calculate_daily_pnl(db, position, current_price)
        
        # Update position fields
        position.last_price = current_price
        position.market_value = market_value_data["market_value"]
        position.unrealized_pnl = market_value_data["unrealized_pnl"]
        position.updated_at = datetime.utcnow()
        
        # Combine all calculation results
        result = {
            **market_value_data,
            **daily_pnl_data,
            "position_id": position.id,
            "symbol": position.symbol,
            "update_timestamp": position.updated_at,
            "success": True
        }
        
        logger.debug(f"Successfully updated market values for {position.symbol}")
        return result
        
    except Exception as e:
        logger.error(f"Error updating market values for position {position.id}: {str(e)}")
        return {
            "position_id": position.id,
            "symbol": position.symbol,
            "success": False,
            "error": str(e)
        }


# Convenience function for bulk position updates
async def bulk_update_position_values(
    db: AsyncSession,
    positions: List[Position]
) -> List[Dict[str, Any]]:
    """
    Bulk update market values for multiple positions
    Efficient batch processing for portfolio-wide updates
    
    Args:
        db: Database session
        positions: List of Position objects to update
        
    Returns:
        List of update results for each position
    """
    if not positions:
        return []
    
    logger.info(f"Starting bulk update for {len(positions)} positions")
    
    # Get unique symbols for batch price fetch
    symbols = list(set(position.symbol for position in positions))
    
    # Fetch all prices in one batch
    prices = await fetch_and_cache_prices(db, symbols)
    
    # Update each position
    results = []
    for position in positions:
        current_price = prices.get(position.symbol)
        
        if current_price is not None:
            result = await update_position_market_values(db, position, current_price)
            results.append(result)
        else:
            logger.warning(f"No price available for {position.symbol}, skipping update")
            results.append({
                "position_id": position.id,
                "symbol": position.symbol,
                "success": False,
                "error": "No price data available"
            })
    
    # Commit all updates
    try:
        await db.commit()
        logger.info(f"Bulk update complete: {len([r for r in results if r.get('success')])} successful")
    except Exception as e:
        logger.error(f"Error committing bulk updates: {str(e)}")
        await db.rollback()
        raise
    
    return results
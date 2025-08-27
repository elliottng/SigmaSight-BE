"""
Market data API endpoints
"""
from datetime import date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.dependencies import get_db, get_current_user
from app.models.users import User
from app.services.market_data_service import market_data_service
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/market-data", tags=["market-data"])


class PriceDataResponse(BaseModel):
    symbol: str
    date: date
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    close: float
    volume: Optional[int]
    sector: Optional[str]
    industry: Optional[str]


class MarketDataRefreshRequest(BaseModel):
    symbols: List[str]
    days_back: Optional[int] = 30
    include_gics: bool = True


class RefreshResponse(BaseModel):
    symbols_processed: int
    symbols_updated: int
    total_records: int
    message: str


@router.get("/prices/{symbol}", response_model=List[PriceDataResponse])
async def get_price_data(
    symbol: str,
    days_back: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical price data for symbol"""
    logger.info(f"Getting price data for {symbol}, {days_back} days back")
    
    try:
        # Get data from cache first
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        cached_prices = await market_data_service.get_cached_prices(
            db=db, 
            symbols=[symbol], 
            target_date=end_date
        )
        
        # If no cached data, fetch from API
        if not cached_prices.get(symbol):
            logger.info(f"No cached data for {symbol}, fetching from API")
            await market_data_service.update_market_data_cache(
                db=db,
                symbols=[symbol],
                start_date=start_date,
                end_date=end_date
            )
        
        # Get cached data after update
        from sqlalchemy import select
        from app.models.market_data import MarketDataCache
        
        stmt = select(MarketDataCache).where(
            MarketDataCache.symbol == symbol.upper(),
            MarketDataCache.date >= start_date,
            MarketDataCache.date <= end_date
        ).order_by(MarketDataCache.date.desc())
        
        result = await db.execute(stmt)
        price_records = result.scalars().all()
        
        return [
            PriceDataResponse(
                symbol=record.symbol,
                date=record.date,
                open=float(record.open) if record.open else None,
                high=float(record.high) if record.high else None,
                low=float(record.low) if record.low else None,
                close=float(record.close),
                volume=record.volume,
                sector=record.sector,
                industry=record.industry
            )
            for record in price_records
        ]
        
    except Exception as e:
        logger.error(f"Error getting price data for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching price data: {str(e)}")


@router.get("/current-prices")
async def get_current_prices(
    symbols: List[str] = Query(..., description="List of symbols to get current prices for"),
    current_user: User = Depends(get_current_user)
):
    """Get current/latest prices for multiple symbols"""
    logger.info(f"Getting current prices for {len(symbols)} symbols")
    
    try:
        current_prices = await market_data_service.fetch_current_prices(symbols)
        return {
            "prices": {
                symbol: float(price) if price else None 
                for symbol, price in current_prices.items()
            },
            "timestamp": date.today().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting current prices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching current prices: {str(e)}")


@router.get("/sectors")
async def get_sector_data(
    symbols: List[str] = Query(..., description="List of symbols to get sector data for"),
    current_user: User = Depends(get_current_user)
):
    """Get GICS sector/industry data for symbols"""
    logger.info(f"Getting sector data for {len(symbols)} symbols")
    
    try:
        gics_data = await market_data_service.fetch_gics_data(symbols)
        return {"gics_data": gics_data}
        
    except Exception as e:
        logger.error(f"Error getting sector data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching sector data: {str(e)}")


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_market_data(
    request: MarketDataRefreshRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger market data refresh for specified symbols"""
    logger.info(f"Refreshing market data for {len(request.symbols)} symbols")
    
    try:
        stats = await market_data_service.bulk_fetch_and_cache(
            db=db,
            symbols=request.symbols,
            days_back=request.days_back
        )
        
        return RefreshResponse(
            symbols_processed=stats['symbols_processed'],
            symbols_updated=stats['symbols_updated'],
            total_records=stats['total_records'],
            message=f"Successfully refreshed market data for {stats['symbols_updated']} symbols"
        )
        
    except Exception as e:
        logger.error(f"Error refreshing market data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error refreshing market data: {str(e)}")


@router.get("/quotes")
async def get_market_quotes(
    symbols: Optional[str] = Query(None, description="Comma-separated list of symbols"),
    current_user: User = Depends(get_current_user)
):
    """Get market quotes for symbols (frontend compatibility endpoint)"""
    logger.info(f"Getting market quotes for symbols: {symbols}")
    
    if not symbols:
        # Return some default symbols if none provided
        default_symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL']
    else:
        default_symbols = [s.strip().upper() for s in symbols.split(',')]
    
    try:
        current_prices = await market_data_service.fetch_current_prices(default_symbols)
        
        # Transform to MarketQuote format expected by frontend
        quotes = []
        for symbol in default_symbols:
            price = current_prices.get(symbol)
            if price:
                quotes.append({
                    "symbol": symbol,
                    "price": float(price),
                    "change": 0.0,  # Mock data - would calculate actual change
                    "change_percent": 0.0,  # Mock data - would calculate actual change
                    "volume": None,
                    "timestamp": date.today().isoformat()
                })
        
        return quotes
        
    except Exception as e:
        logger.error(f"Error getting market quotes: {str(e)}")
        # Return mock data on error to keep frontend working
        quotes = []
        for symbol in default_symbols:
            quotes.append({
                "symbol": symbol,
                "price": 100.0,  # Mock price
                "change": 0.0,
                "change_percent": 0.0,
                "volume": None,
                "timestamp": date.today().isoformat()
            })
        return quotes


@router.get("/options/{symbol}")
async def get_options_chain(
    symbol: str,
    expiration_date: Optional[date] = Query(None, description="Specific expiration date"),
    current_user: User = Depends(get_current_user)
):
    """Get options chain data for symbol"""
    logger.info(f"Getting options chain for {symbol}")
    
    try:
        options_data = await market_data_service.fetch_options_chain(
            symbol=symbol,
            expiration_date=expiration_date
        )
        
        return {
            "symbol": symbol,
            "options_count": len(options_data),
            "options": options_data
        }
        
    except Exception as e:
        logger.error(f"Error getting options chain for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching options chain: {str(e)}")

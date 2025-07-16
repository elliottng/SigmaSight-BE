"""
Market Data Service - Handles external market data APIs (Polygon.io, YFinance)
"""
import asyncio
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any
from polygon import RESTClient
import yfinance as yf
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.config import settings
from app.models.market_data import MarketDataCache
from app.core.logging import get_logger
from app.services.rate_limiter import polygon_rate_limiter, ExponentialBackoff

logger = get_logger(__name__)


class MarketDataService:
    """Service for fetching and managing market data from external APIs"""
    
    def __init__(self):
        self.polygon_client = RESTClient(api_key=settings.POLYGON_API_KEY)
        self._cache: Dict[str, Any] = {}
    
    async def fetch_stock_prices(
        self, 
        symbols: List[str], 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch stock price data from Polygon.io
        
        Args:
            symbols: List of stock symbols
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            Dictionary with symbol as key and list of price data as value
        """
        logger.info(f"Fetching stock prices for {len(symbols)} symbols")
        
        if not start_date:
            start_date = date.today() - timedelta(days=90)
        if not end_date:
            end_date = date.today()
            
        results = {}
        
        for symbol in symbols:
            try:
                # Apply rate limiting before API call
                await polygon_rate_limiter.acquire()
                
                # Get daily bars from Polygon with pagination support
                all_bars = []
                next_url = None
                page_count = 0
                
                while True:
                    page_count += 1
                    
                    if next_url:
                        # Fetch next page using pagination URL
                        await polygon_rate_limiter.acquire()
                        response = self.polygon_client._get_raw(next_url)
                    else:
                        # Initial request
                        response = self.polygon_client.get_aggs(
                            ticker=symbol.upper(),
                            multiplier=1,
                            timespan="day",
                            from_=start_date.strftime("%Y-%m-%d"),
                            to=end_date.strftime("%Y-%m-%d"),
                            adjusted=True,
                            sort="asc",
                            limit=50000,
                            raw=True  # Get raw response to check for pagination
                        )
                    
                    # Extract bars from response
                    if hasattr(response, 'results'):
                        bars = response.results
                    elif isinstance(response, dict) and 'results' in response:
                        bars = response['results']
                    else:
                        # Fallback for non-paginated response
                        bars = response
                        all_bars.extend(bars)
                        break
                    
                    all_bars.extend(bars)
                    
                    # Check for pagination
                    if hasattr(response, 'next_url') and response.next_url:
                        next_url = response.next_url
                        logger.debug(f"Fetching page {page_count + 1} for {symbol}")
                    elif isinstance(response, dict) and response.get('next_url'):
                        next_url = response['next_url']
                        logger.debug(f"Fetching page {page_count + 1} for {symbol}")
                    else:
                        break
                
                # Process all bars
                price_data = []
                for bar in all_bars:
                    # Handle both object and dict formats
                    if hasattr(bar, 'timestamp'):
                        timestamp = bar.timestamp
                        open_price = bar.open
                        high_price = bar.high
                        low_price = bar.low
                        close_price = bar.close
                        volume = bar.volume
                    else:
                        timestamp = bar['t']
                        open_price = bar['o']
                        high_price = bar['h']
                        low_price = bar['l']
                        close_price = bar['c']
                        volume = bar['v']
                    
                    price_data.append({
                        'symbol': symbol.upper(),
                        'date': datetime.fromtimestamp(timestamp / 1000).date(),
                        'open': Decimal(str(open_price)),
                        'high': Decimal(str(high_price)),
                        'low': Decimal(str(low_price)),
                        'close': Decimal(str(close_price)),
                        'volume': volume,
                        'data_source': 'polygon'
                    })
                
                results[symbol] = price_data
                logger.info(f"Fetched {len(price_data)} price records for {symbol} across {page_count} page(s)")
                
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
                results[symbol] = []
        
        return results
    
    async def fetch_current_prices(self, symbols: List[str]) -> Dict[str, Decimal]:
        """
        Fetch current/latest prices for symbols
        
        Args:
            symbols: List of symbols to fetch prices for
            
        Returns:
            Dictionary with symbol as key and current price as value
        """
        logger.info(f"Fetching current prices for {len(symbols)} symbols")
        current_prices = {}
        
        for symbol in symbols:
            try:
                # Apply rate limiting before API call
                await polygon_rate_limiter.acquire()
                
                # Get last trade from Polygon
                last_trade = self.polygon_client.get_last_trade(ticker=symbol.upper())
                if last_trade:
                    current_prices[symbol] = Decimal(str(last_trade.price))
                    logger.debug(f"Current price for {symbol}: {last_trade.price}")
                
            except Exception as e:
                logger.error(f"Error fetching current price for {symbol}: {str(e)}")
                # Fallback to last cached price if available
                current_prices[symbol] = None
        
        return current_prices
    
    async def fetch_gics_data(self, symbols: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Fetch GICS sector/industry data from YFinance
        
        Args:
            symbols: List of symbols to fetch GICS data for
            
        Returns:
            Dictionary with symbol as key and sector/industry info as value
        """
        logger.info(f"Fetching GICS data for {len(symbols)} symbols")
        gics_data = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol.upper())
                info = ticker.info
                
                gics_data[symbol] = {
                    'sector': info.get('sector'),
                    'industry': info.get('industry')
                }
                
                logger.debug(f"GICS data for {symbol}: {gics_data[symbol]}")
                
                # Add delay to be respectful to YFinance
                await asyncio.sleep(0.2)
                
            except Exception as e:
                logger.error(f"Error fetching GICS data for {symbol}: {str(e)}")
                gics_data[symbol] = {'sector': None, 'industry': None}
        
        return gics_data
    
    async def fetch_options_chain(
        self, 
        symbol: str, 
        expiration_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch options chain data from Polygon.io
        
        Args:
            symbol: Underlying symbol
            expiration_date: Specific expiration date (optional)
            
        Returns:
            List of option contract data
        """
        logger.info(f"Fetching options chain for {symbol}")
        
        try:
            # Apply rate limiting before API call
            await polygon_rate_limiter.acquire()
            
            # Get options contracts with pagination support
            all_contracts = []
            next_url = None
            page_count = 0
            
            while True:
                page_count += 1
                
                if next_url:
                    # Fetch next page
                    await polygon_rate_limiter.acquire()
                    response = self.polygon_client._get_raw(next_url)
                    if isinstance(response, dict) and 'results' in response:
                        contracts = response['results']
                        next_url = response.get('next_url')
                    else:
                        break
                else:
                    # Initial request
                    if expiration_date:
                        exp_date_str = expiration_date.strftime("%Y-%m-%d")
                        contracts = self.polygon_client.list_options_contracts(
                            underlying_ticker=symbol.upper(),
                            expiration_date=exp_date_str,
                            limit=1000
                        )
                    else:
                        contracts = self.polygon_client.list_options_contracts(
                            underlying_ticker=symbol.upper(),
                            limit=1000
                        )
                    
                    # Check if this is a paginated response
                    if hasattr(contracts, '__iter__'):
                        all_contracts.extend(contracts)
                        break  # No pagination in current response format
                
                all_contracts.extend(contracts)
                
                if not next_url:
                    break
                
                logger.debug(f"Fetching page {page_count + 1} of options contracts for {symbol}")
            
            options_data = []
            for contract in all_contracts:
                options_data.append({
                    'ticker': contract.ticker,
                    'underlying_ticker': contract.underlying_ticker,
                    'expiration_date': datetime.strptime(contract.expiration_date, "%Y-%m-%d").date(),
                    'strike_price': Decimal(str(contract.strike_price)),
                    'contract_type': contract.contract_type,  # 'call' or 'put'
                    'exercise_style': getattr(contract, 'exercise_style', 'american'),
                })
            
            logger.info(f"Fetched {len(options_data)} option contracts for {symbol} across {page_count} page(s)")
            return options_data
            
        except Exception as e:
            logger.error(f"Error fetching options chain for {symbol}: {str(e)}")
            return []
    
    async def update_market_data_cache(
        self, 
        db: AsyncSession, 
        symbols: List[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        include_gics: bool = True
    ) -> Dict[str, int]:
        """
        Update market data cache with latest price and GICS data
        
        Args:
            db: Database session
            symbols: List of symbols to update
            start_date: Start date for historical data
            end_date: End date for historical data
            include_gics: Whether to fetch GICS sector/industry data
            
        Returns:
            Dictionary with update statistics
        """
        logger.info(f"Updating market data cache for {len(symbols)} symbols")
        
        # Fetch price data
        price_data = await self.fetch_stock_prices(symbols, start_date, end_date)
        
        # Fetch GICS data if requested
        gics_data = {}
        if include_gics:
            gics_data = await self.fetch_gics_data(symbols)
        
        total_records = 0
        updated_symbols = 0
        
        for symbol, prices in price_data.items():
            if not prices:
                continue
                
            # Get GICS data for this symbol
            symbol_gics = gics_data.get(symbol, {})
            
            # Prepare records for upsert
            records_to_upsert = []
            for price_record in prices:
                record = {
                    **price_record,
                    'sector': symbol_gics.get('sector'),
                    'industry': symbol_gics.get('industry')
                }
                records_to_upsert.append(record)
            
            if records_to_upsert:
                # Use PostgreSQL UPSERT (ON CONFLICT DO UPDATE)
                stmt = pg_insert(MarketDataCache).values(records_to_upsert)
                stmt = stmt.on_conflict_do_update(
                    constraint='uq_market_data_cache_symbol_date',
                    set_={
                        'open': stmt.excluded.open,
                        'high': stmt.excluded.high,
                        'low': stmt.excluded.low,
                        'close': stmt.excluded.close,
                        'volume': stmt.excluded.volume,
                        'sector': stmt.excluded.sector,
                        'industry': stmt.excluded.industry,
                        'updated_at': datetime.utcnow()
                    }
                )
                
                await db.execute(stmt)
                total_records += len(records_to_upsert)
                updated_symbols += 1
        
        await db.commit()
        
        stats = {
            'symbols_processed': len(symbols),
            'symbols_updated': updated_symbols,
            'total_records': total_records
        }
        
        logger.info(f"Market data cache update complete: {stats}")
        return stats
    
    async def get_cached_prices(
        self, 
        db: AsyncSession, 
        symbols: List[str], 
        target_date: Optional[date] = None
    ) -> Dict[str, Optional[Decimal]]:
        """
        Get cached prices for symbols on a specific date
        
        Args:
            db: Database session
            symbols: List of symbols
            target_date: Date to get prices for (defaults to latest available)
            
        Returns:
            Dictionary with symbol as key and price as value
        """
        if not target_date:
            target_date = date.today()
        
        # Query cached prices
        stmt = select(MarketDataCache).where(
            MarketDataCache.symbol.in_([s.upper() for s in symbols]),
            MarketDataCache.date <= target_date
        ).order_by(MarketDataCache.symbol, MarketDataCache.date.desc())
        
        result = await db.execute(stmt)
        cached_data = result.scalars().all()
        
        # Group by symbol and get most recent price
        prices = {}
        for symbol in symbols:
            symbol_upper = symbol.upper()
            symbol_data = [d for d in cached_data if d.symbol == symbol_upper]
            if symbol_data:
                prices[symbol] = symbol_data[0].close
            else:
                prices[symbol] = None
        
        return prices
    
    async def bulk_fetch_and_cache(
        self, 
        db: AsyncSession, 
        symbols: List[str],
        days_back: int = 90
    ) -> Dict[str, Any]:
        """
        Bulk fetch historical data and cache for multiple symbols
        
        Args:
            db: Database session
            symbols: List of symbols to fetch
            days_back: Number of days of historical data to fetch
            
        Returns:
            Summary statistics of the operation
        """
        start_date = date.today() - timedelta(days=days_back)
        end_date = date.today()
        
        logger.info(f"Bulk fetching {days_back} days of data for {len(symbols)} symbols")
        
        return await self.update_market_data_cache(
            db=db,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            include_gics=True
        )


# Global service instance
market_data_service = MarketDataService()
"""
Market Data Service - Handles external market data APIs (Polygon.io, YFinance, FMP, TradeFeeds)
Updated for Section 1.4.9 - Hybrid provider approach with mutual fund holdings support
"""
import asyncio
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any
from polygon import RESTClient
# import yfinance as yf  # Removed - using FMP primary architecture
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.config import settings
from app.models.market_data import MarketDataCache
from app.core.logging import get_logger
from app.services.rate_limiter import polygon_rate_limiter, ExponentialBackoff
from app.clients import market_data_factory, DataType

logger = get_logger(__name__)


class MarketDataService:
    """Service for fetching and managing market data from external APIs"""
    
    def __init__(self):
        self.polygon_client = RESTClient(api_key=settings.POLYGON_API_KEY)
        self._cache: Dict[str, Any] = {}
        # Initialize the market data factory
        market_data_factory.initialize()
    
    # New hybrid provider methods (Section 1.4.9)
    
    async def fetch_historical_data_hybrid(
        self, 
        symbols: List[str], 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch historical stock price data using hybrid provider approach
        
        Priority: FMP -> Polygon (fallback)
        
        Args:
            symbols: List of stock symbols
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            Dictionary with symbol as key and list of price data as value
        """
        logger.info(f"Fetching historical data (hybrid) for {len(symbols)} symbols")
        
        if not start_date:
            start_date = date.today() - timedelta(days=90)
        if not end_date:
            end_date = date.today()
        
        days_back = (end_date - start_date).days
        
        # Separate options from stocks/ETFs
        # Options symbols typically have 15+ characters and contain expiration dates
        options_symbols = [s for s in symbols if len(s) > 10 and any(c.isdigit() for c in s[6:])]
        stock_symbols = [s for s in symbols if s not in options_symbols]
        
        results = {}
        
        # Process stocks/ETFs with FMP
        if stock_symbols:
            provider = market_data_factory.get_provider_for_data_type(DataType.STOCKS)
            if provider:
                try:
                    for symbol in stock_symbols:
                        try:
                            historical_data = await provider.get_historical_prices(symbol, days=days_back)
                            
                            if historical_data:
                                # Convert FMP format to our standard format
                                price_records = []
                                for day_data in historical_data:
                                    # Handle date field - could be string or date object
                                    date_value = day_data['date']
                                    if isinstance(date_value, str):
                                        date_obj = datetime.strptime(date_value, '%Y-%m-%d').date()
                                    elif isinstance(date_value, date):
                                        date_obj = date_value
                                    else:
                                        date_obj = datetime.fromisoformat(str(date_value)).date()
                                    
                                    price_records.append({
                                        'symbol': symbol.upper(),
                                        'date': date_obj,
                                        'open': Decimal(str(day_data['open'])),
                                        'high': Decimal(str(day_data['high'])),
                                        'low': Decimal(str(day_data['low'])),
                                        'close': Decimal(str(day_data['close'])),
                                        'volume': day_data['volume'],
                                        'data_source': 'fmp'
                                    })
                                
                                results[symbol] = price_records
                                logger.debug(f"FMP: Retrieved {len(price_records)} records for {symbol}")
                            else:
                                results[symbol] = []
                                
                        except Exception as e:
                            logger.warning(f"FMP error for {symbol}: {str(e)}")
                            results[symbol] = []
                
                    # Check success rate for stocks only
                    successful_stocks = [s for s in stock_symbols if results.get(s)]
                    stock_success_rate = len(successful_stocks) / len(stock_symbols) if stock_symbols else 0
                    
                    if stock_success_rate >= 0.8:  # 80% success rate threshold
                        logger.info(f"FMP historical data: {len(successful_stocks)}/{len(stock_symbols)} stocks ({stock_success_rate:.1%})")
                    else:
                        logger.warning(f"FMP stock success rate low ({stock_success_rate:.1%}), using Polygon fallback for failed symbols")
                        
                except Exception as e:
                    logger.error(f"FMP historical data provider error: {str(e)}")
        
        # Process options and any failed stocks with Polygon
        symbols_for_polygon = options_symbols + [s for s in stock_symbols if not results.get(s)]
        
        if symbols_for_polygon:
            logger.info(f"Using Polygon for {len(options_symbols)} options and {len(symbols_for_polygon) - len(options_symbols)} failed stocks")
            polygon_results = await self.fetch_stock_prices(symbols_for_polygon, start_date, end_date)
            
            # Merge Polygon results
            for symbol in symbols_for_polygon:
                results[symbol] = polygon_results.get(symbol, [])
        
        return results

    async def fetch_stock_prices_hybrid(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch current stock prices using hybrid provider approach
        
        Priority: FMP -> TradeFeeds -> Polygon (fallback)
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary with symbol as key and price data as value
        """
        logger.info(f"Fetching stock prices (hybrid) for {len(symbols)} symbols")
        
        # Try FMP first
        provider = market_data_factory.get_provider_for_data_type(DataType.STOCKS)
        if provider:
            try:
                result = await provider.get_stock_prices(symbols)
                if result:
                    logger.info(f"Successfully fetched {len(result)} stock prices from {provider.provider_name}")
                    return result
            except Exception as e:
                logger.error(f"Error fetching stock prices from {provider.provider_name}: {str(e)}")
        
        # Fallback to current Polygon implementation
        logger.warning("Falling back to Polygon for stock prices")
        current_prices = await self.fetch_current_prices(symbols)
        
        # Convert to hybrid format
        result = {}
        for symbol, price in current_prices.items():
            if price is not None:
                result[symbol] = {
                    'price': price,
                    'change': Decimal('0'),  # Not available from current implementation
                    'change_percent': Decimal('0'),
                    'volume': 0,
                    'timestamp': datetime.now(),
                    'provider': 'Polygon (fallback)'
                }
        
        return result
    
    async def fetch_mutual_fund_holdings(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Fetch mutual fund holdings using hybrid provider approach
        
        Priority: FMP -> TradeFeeds
        
        Args:
            symbol: Mutual fund symbol (e.g., 'FXNAX')
            
        Returns:
            List of fund holdings
        """
        logger.info(f"Fetching mutual fund holdings for {symbol}")
        
        provider = market_data_factory.get_provider_for_data_type(DataType.FUNDS)
        if provider:
            try:
                holdings = await provider.get_fund_holdings(symbol)
                logger.info(f"Successfully fetched {len(holdings)} holdings for {symbol} from {provider.provider_name}")
                return holdings
            except Exception as e:
                logger.error(f"Error fetching fund holdings for {symbol} from {provider.provider_name}: {str(e)}")
                raise
        else:
            logger.error("No provider available for mutual fund holdings")
            raise Exception("No mutual fund holdings provider configured")
    
    async def fetch_etf_holdings(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Fetch ETF holdings using hybrid provider approach
        
        Uses same endpoint as mutual funds for most providers
        
        Args:
            symbol: ETF symbol (e.g., 'VTI', 'SPY')
            
        Returns:
            List of ETF holdings
        """
        logger.info(f"Fetching ETF holdings for {symbol}")
        return await self.fetch_mutual_fund_holdings(symbol)  # Same endpoint for most providers
    
    async def validate_fund_holdings(self, holdings: List[Dict[str, Any]], symbol: str) -> Dict[str, Any]:
        """
        Validate fund holdings data quality
        
        Args:
            holdings: List of holdings data
            symbol: Fund symbol for logging
            
        Returns:
            Validation results
        """
        total_weight = sum(h.get('weight', 0) for h in holdings)
        complete_holdings = [h for h in holdings if h.get('symbol') and h.get('name')]
        
        validation = {
            'symbol': symbol,
            'total_holdings': len(holdings),
            'complete_holdings': len(complete_holdings),
            'total_weight': float(total_weight),
            'weight_percentage': float(total_weight * 100),
            'data_quality': 'good' if total_weight >= 0.9 else 'partial',
            'completeness': len(complete_holdings) / len(holdings) if holdings else 0
        }
        
        logger.info(f"Fund holdings validation for {symbol}: {validation['total_holdings']} holdings, "
                   f"{validation['weight_percentage']:.1f}% weight coverage, "
                   f"{validation['data_quality']} quality")
        
        return validation
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """
        Get status of all configured market data providers
        
        Returns:
            Dictionary with provider status information
        """
        logger.info("Checking market data provider status")
        
        # Get available providers
        providers = market_data_factory.get_available_providers()
        
        # Validate API keys
        validation_results = await market_data_factory.validate_all_providers()
        
        status = {
            'providers_configured': len(providers),
            'providers_active': sum(validation_results.values()),
            'provider_details': {}
        }
        
        for name, info in providers.items():
            status['provider_details'][name] = {
                **info,
                'api_key_valid': validation_results.get(name, False),
                'status': 'active' if validation_results.get(name, False) else 'inactive'
            }
        
        # Add configuration settings
        status['configuration'] = {
            'use_fmp_for_stocks': settings.USE_FMP_FOR_STOCKS,
            'use_fmp_for_funds': settings.USE_FMP_FOR_FUNDS,
            'polygon_available': bool(settings.POLYGON_API_KEY),
            'fmp_configured': bool(settings.FMP_API_KEY),
            'tradefeeds_configured': bool(settings.TRADEFEEDS_API_KEY)
        }
        
        logger.info(f"Provider status: {status['providers_active']}/{status['providers_configured']} active")
        return status
    
    # Legacy methods (maintained for backward compatibility)
    
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
        Fetch GICS sector/industry data 
        
        NOTE: YFinance removed for FMP-primary architecture. 
        GICS data temporarily disabled until FMP coverage improves.
        
        Args:
            symbols: List of symbols to fetch GICS data for
            
        Returns:
            Dictionary with symbol as key and sector/industry info as value
        """
        logger.warning(f"GICS data temporarily disabled - YFinance removed for FMP migration")
        logger.info(f"Returning empty GICS data for {len(symbols)} symbols")
        
        # Return empty GICS data - system handles missing data gracefully
        gics_data = {}
        for symbol in symbols:
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
        
        # Fetch price data using hybrid approach (FMP primary, Polygon fallback)
        price_data = await self.fetch_historical_data_hybrid(symbols, start_date, end_date)
        
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
    
    
    async def fetch_company_profiles(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch company profiles including sector and industry data from FMP
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary with symbol as key and profile data including sector/industry
        """
        logger.info(f"Fetching company profiles for {len(symbols)} symbols")
        
        results = {}
        
        try:
            # Get FMP provider for stocks/ETFs
            provider = market_data_factory.get_provider_for_data_type(DataType.STOCKS)
            
            if provider and hasattr(provider, 'get_company_profile'):
                # Process in batches of 100 symbols (FMP limit)
                batch_size = 100
                for i in range(0, len(symbols), batch_size):
                    batch = symbols[i:i + batch_size]
                    
                    try:
                        batch_profiles = await provider.get_company_profile(batch)
                        results.update(batch_profiles)
                        logger.info(f"Retrieved profiles for {len(batch_profiles)}/{len(batch)} symbols in batch")
                    except Exception as e:
                        logger.error(f"Failed to fetch profiles for batch {i//batch_size + 1}: {str(e)}")
                        continue
                
                logger.info(f"Successfully retrieved {len(results)} company profiles")
            else:
                logger.warning("FMP provider not available or doesn't support company profiles")
                
        except Exception as e:
            logger.error(f"Error fetching company profiles: {str(e)}")
        
        return results
    
    async def update_security_metadata(
        self, 
        db: AsyncSession,
        symbols: List[str],
        force_refresh: bool = False
    ) -> Dict[str, bool]:
        """
        Update market_data_cache with sector/industry metadata from FMP profiles
        
        Args:
            db: Database session
            symbols: List of symbols to update
            force_refresh: Force refresh even if data exists
            
        Returns:
            Dictionary with symbol as key and success status
        """
        logger.info(f"Updating security metadata for {len(symbols)} symbols")
        
        results = {}
        
        try:
            # Check existing cache entries if not forcing refresh
            if not force_refresh:
                stmt = select(MarketDataCache).where(
                    MarketDataCache.symbol.in_(symbols),
                    MarketDataCache.sector.isnot(None)
                )
                existing = await db.execute(stmt)
                existing_symbols = {row.symbol for row in existing.scalars()}
                
                # Only fetch missing symbols
                symbols_to_fetch = [s for s in symbols if s not in existing_symbols]
                logger.info(f"Found {len(existing_symbols)} cached, fetching {len(symbols_to_fetch)} new")
            else:
                symbols_to_fetch = symbols
            
            if not symbols_to_fetch:
                return {s: True for s in symbols}
            
            # Fetch company profiles
            profiles = await self.fetch_company_profiles(symbols_to_fetch)
            
            # Update database - use today's date as a reference point for metadata
            reference_date = date.today()
            
            for symbol, profile in profiles.items():
                try:
                    # Prepare upsert statement with date field for unique constraint
                    stmt = pg_insert(MarketDataCache).values(
                        symbol=symbol,
                        date=reference_date,  # Use today's date for metadata record
                        close=Decimal('0'),  # Required field, use 0 as placeholder
                        sector=profile.get('sector'),
                        industry=profile.get('industry'),
                        exchange=profile.get('exchange'),
                        country=profile.get('country'),
                        market_cap=profile.get('market_cap'),
                        data_source='fmp_profile',  # Mark as profile data
                        updated_at=datetime.utcnow()
                    )
                    
                    # On conflict, update the metadata fields
                    stmt = stmt.on_conflict_do_update(
                        constraint='uq_market_data_cache_symbol_date',
                        set_={
                            'sector': stmt.excluded.sector,
                            'industry': stmt.excluded.industry,
                            'exchange': stmt.excluded.exchange,
                            'country': stmt.excluded.country,
                            'market_cap': stmt.excluded.market_cap,
                            'data_source': stmt.excluded.data_source,
                            'updated_at': stmt.excluded.updated_at
                        }
                    )
                    
                    await db.execute(stmt)
                    results[symbol] = True
                    
                except Exception as e:
                    logger.error(f"Failed to update metadata for {symbol}: {str(e)}")
                    results[symbol] = False
            
            # Mark symbols without profiles as processed (but unsuccessful)
            for symbol in symbols_to_fetch:
                if symbol not in results:
                    results[symbol] = False
            
            await db.commit()
            
            success_count = sum(1 for v in results.values() if v)
            logger.info(f"Updated metadata for {success_count}/{len(symbols_to_fetch)} symbols")
            
        except Exception as e:
            logger.error(f"Error updating security metadata: {str(e)}")
            await db.rollback()
            return {s: False for s in symbols}
        
        return results
    
    async def close(self):
        """Close all provider client sessions"""
        await market_data_factory.close_all()
        logger.info("MarketDataService: All provider sessions closed")


# Global service instance
market_data_service = MarketDataService()
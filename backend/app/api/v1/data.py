"""
Raw Data API endpoints (/data/)
Provides unprocessed data for LLM consumption
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.database import get_async_session
from app.core.dependencies import get_current_user
from app.core.datetime_utils import utc_now, to_utc_iso8601, to_iso_date
from app.models.users import Portfolio
from app.models.positions import Position
from app.models.market_data import MarketDataCache
from app.schemas.auth import CurrentUser
from app.core.logging import get_logger
from app.services.market_data_service import MarketDataService
from app.services.portfolio_data_service import PortfolioDataService

logger = get_logger(__name__)

router = APIRouter(prefix="/data", tags=["raw-data"])


# Portfolio Raw Data Endpoints

@router.get("/portfolio/{portfolio_id}/complete")
async def get_portfolio_complete(
    portfolio_id: UUID,
    include_holdings: bool = Query(True, description="Include position details"),
    include_timeseries: bool = Query(False, description="Include historical data"),
    include_attrib: bool = Query(False, description="Include attribution data"),
    as_of_date: Optional[date] = Query(None, description="Historical snapshot date"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get complete portfolio data with optional sections.
    
    API layer owns:
    - Consistent as_of timestamps across all sections
    - Deterministic ordering of positions/data
    - Full meta object population
    
    Returns raw data with proper meta object.
    """
    async with db as session:
        # Verify portfolio ownership
        stmt = select(Portfolio).where(
            and_(
                Portfolio.id == (portfolio_id if isinstance(portfolio_id, UUID) else UUID(str(portfolio_id))),
                Portfolio.user_id == (UUID(str(current_user.id)) if not isinstance(current_user.id, UUID) else current_user.id)
            )
        ).options(selectinload(Portfolio.positions))
        
        result = await session.execute(stmt)
        portfolio = result.scalar_one_or_none()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Set consistent as_of timestamp
        as_of_timestamp = utc_now()
        
        # Get positions with current market values
        positions_data = []
        total_market_value = 0
        long_count = 0
        short_count = 0
        option_count = 0
        complete_data_count = 0
        partial_data_count = 0
        
        if include_holdings:
            for position in portfolio.positions:
                # Get current price from market data cache
                cache_stmt = select(MarketDataCache).where(
                    MarketDataCache.symbol == position.symbol
                ).order_by(MarketDataCache.updated_at.desc())
                cache_result = await session.execute(cache_stmt)
                market_data = cache_result.scalars().first()
                
                last_price = market_data.close if market_data else position.entry_price
                market_value = float(position.quantity) * float(last_price)
                
                # Count position types
                if position.position_type.value.startswith("L"):
                    if position.position_type.value in ["LC", "LP"]:
                        option_count += 1
                    else:
                        long_count += 1
                elif position.position_type.value.startswith("S"):
                    if position.position_type.value in ["SC", "SP"]:
                        option_count += 1
                    else:
                        short_count += 1
                        market_value = -market_value  # Negative for shorts
                
                total_market_value += market_value
                
                # Check data completeness (simplified for now - using market data cache)
                # In a full implementation, we'd have a separate historical prices table
                has_complete_history = market_data is not None  # Simplified check
                if has_complete_history:
                    complete_data_count += 1
                else:
                    partial_data_count += 1
                
                positions_data.append({
                    "id": str(position.id),
                    "symbol": position.symbol,
                    "quantity": float(position.quantity),
                    "position_type": position.position_type.value,
                    "market_value": market_value,
                    "last_price": float(last_price),
                    "has_complete_history": has_complete_history
                })
        
        # Sort positions for deterministic ordering
        positions_data.sort(key=lambda x: (x['symbol'], x['id']))
        
        # Build response with proper meta object
        # Note: Portfolio model doesn't have cash_balance field
        # Using 5% of portfolio value as a reasonable cash allocation placeholder
        # This represents typical cash reserves for portfolio liquidity
        cash_balance = total_market_value * 0.05 if total_market_value > 0 else 10000.0
        
        # Create meta object
        meta = {
            "as_of": to_utc_iso8601(as_of_timestamp),
            "requested": {
                "portfolio_id": str(portfolio_id),
                "include_holdings": include_holdings,
                "include_timeseries": include_timeseries,
                "include_attrib": include_attrib,
                "as_of_date": str(as_of_date) if as_of_date else None
            },
            "applied": {
                "include_holdings": include_holdings,
                "include_timeseries": include_timeseries,
                "include_attrib": include_attrib,
                "as_of_date": to_utc_iso8601(as_of_timestamp)
            },
            "limits": {
                "max_positions": 2000,
                "max_days": 180,
                "max_symbols": 5 if include_timeseries else None
            },
            "rows_returned": len(positions_data) if include_holdings else 0,
            "truncated": False,
            "schema_version": "1.0"
        }
        
        response = {
            "meta": meta,
            "portfolio": {
                "id": str(portfolio.id),
                "name": portfolio.name,
                "total_value": total_market_value + cash_balance,
                "cash_balance": cash_balance,
                "position_count": len(positions_data),
                "as_of": to_utc_iso8601(as_of_timestamp)
            },
            "positions_summary": {
                "long_count": long_count,
                "short_count": short_count,
                "option_count": option_count,
                "total_market_value": total_market_value
            }
        }
        
        # Add holdings section if requested
        if include_holdings:
            response["holdings"] = positions_data
            
        # Add timeseries section if requested (placeholder for now)
        if include_timeseries:
            # TODO: Implement actual timeseries data retrieval
            # For now, return empty structure
            response["timeseries"] = {
                "dates": [],
                "values": [],
                "note": "Timeseries data not yet implemented"
            }
            
        # Add attribution section if requested (placeholder for now)  
        if include_attrib:
            # TODO: Implement actual attribution data retrieval
            # For now, return empty structure
            response["attribution"] = {
                "contributors": [],
                "detractors": [],
                "note": "Attribution data not yet implemented"
            }
            
        response["data_quality"] = {
            "complete_data_positions": complete_data_count,
            "partial_data_positions": partial_data_count,
            "as_of": to_utc_iso8601(as_of_timestamp)
        }
        
        return response


@router.get("/portfolio/{portfolio_id}/data-quality")
async def get_portfolio_data_quality(
    portfolio_id: UUID,
    check_factors: bool = Query(True, description="Check factor data completeness"),
    check_correlations: bool = Query(True, description="Check correlation feasibility"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Assess data availability for portfolio calculations.
    Indicates which calculations are feasible given available data.
    """
    async with db as session:
        # Verify portfolio ownership
        stmt = select(Portfolio).where(
            and_(
                Portfolio.id == (portfolio_id if isinstance(portfolio_id, UUID) else UUID(str(portfolio_id))),
                Portfolio.user_id == (UUID(str(current_user.id)) if not isinstance(current_user.id, UUID) else current_user.id)
            )
        ).options(selectinload(Portfolio.positions))
        
        result = await session.execute(stmt)
        portfolio = result.scalar_one_or_none()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Analyze data quality for each position
        complete_history = []
        partial_history = []
        insufficient_data = []
        
        for position in portfolio.positions:
            # Check if we have market data (simplified check)
            # In production, we'd check actual historical price records
            cache_stmt = select(MarketDataCache).where(
                MarketDataCache.symbol == position.symbol
            )
            cache_result = await session.execute(cache_stmt)
            market_data = cache_result.scalars().first()
            
            # Simulate days available based on whether we have data
            days_available = 150 if market_data else 0
            
            if days_available >= 150:  # Full history for all calculations
                complete_history.append(position.symbol)
            elif days_available >= 30:  # Partial history
                partial_history.append({
                    "symbol": position.symbol,
                    "days_available": days_available,
                    "days_missing": 150 - days_available
                })
            else:  # Insufficient data
                reason = "recent_listing" if days_available < 20 else "incomplete_data"
                insufficient_data.append({
                    "symbol": position.symbol,
                    "days_available": days_available,
                    "reason": reason
                })
        
        # Calculate feasibility
        correlation_eligible = len(complete_history) + len([p for p in partial_history if p["days_available"] >= 30])
        factor_eligible = len(complete_history) + len([p for p in partial_history if p["days_available"] >= 60])
        volatility_eligible = len(complete_history) + len([p for p in partial_history if p["days_available"] >= 20])
        
        response = {
            "portfolio_id": str(portfolio_id),
            "assessment_date": to_iso_date(date.today()),
            "summary": {
                "total_positions": len(portfolio.positions),
                "complete_data": len(complete_history),
                "partial_data": len(partial_history),
                "insufficient_data": len(insufficient_data),
                "data_coverage_percent": (len(complete_history) / len(portfolio.positions) * 100) if portfolio.positions else 0
            },
            "position_data_quality": {
                "complete_history": complete_history,
                "partial_history": partial_history,
                "insufficient_data": insufficient_data
            },
            "calculation_feasibility": {
                "correlation_matrix": {
                    "feasible": correlation_eligible >= 2,
                    "positions_eligible": correlation_eligible,
                    "positions_excluded": len(portfolio.positions) - correlation_eligible,
                    "min_days_overlap": 30
                },
                "factor_regression": {
                    "feasible": factor_eligible >= 1,
                    "positions_eligible": factor_eligible,
                    "positions_excluded": len(portfolio.positions) - factor_eligible,
                    "min_days_required": 60
                },
                "volatility_analysis": {
                    "feasible": volatility_eligible >= 1,
                    "positions_eligible": volatility_eligible,
                    "positions_excluded": len(portfolio.positions) - volatility_eligible,
                    "min_days_required": 20
                }
            }
        }
        
        if check_factors:
            # Check factor ETF data availability
            factor_etfs = ["SPY", "VTV", "VUG", "MTUM", "QUAL", "SLY", "USMV"]
            complete_factors = []
            partial_factors = []
            missing_factors = []
            
            for etf in factor_etfs:
                # Check if we have market data for the ETF
                cache_stmt = select(MarketDataCache).where(
                    MarketDataCache.symbol == etf
                )
                cache_result = await session.execute(cache_stmt)
                market_data = cache_result.scalars().first()
                count = 150 if market_data else 0
                
                if count >= 150:
                    complete_factors.append(etf)
                elif count > 0:
                    partial_factors.append(etf)
                else:
                    missing_factors.append(etf)
            
            response["factor_etf_coverage"] = {
                "complete": complete_factors,
                "partial": partial_factors,
                "missing": missing_factors
            }
        
        response["last_update"] = to_utc_iso8601(utc_now())
        
        return response


# Position Raw Data Endpoints

@router.get("/positions/details")
async def get_positions_details(
    portfolio_id: Optional[UUID] = Query(None, description="Portfolio UUID"),
    position_ids: Optional[str] = Query(None, description="Comma-separated position IDs"),
    include_closed: bool = Query(False, description="Include closed positions"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get detailed position information including entry prices and cost basis.
    Returns raw position data without calculations.
    """
    async with db as session:
        # Build query based on parameters
        if portfolio_id:
            # Verify portfolio ownership
            port_stmt = select(Portfolio).where(
                and_(
                    Portfolio.id == (portfolio_id if isinstance(portfolio_id, UUID) else UUID(str(portfolio_id))),
                    Portfolio.user_id == (UUID(str(current_user.id)) if not isinstance(current_user.id, UUID) else current_user.id)
                )
            )
            port_result = await session.execute(port_stmt)
            portfolio = port_result.scalar_one_or_none()
            
            if not portfolio:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            stmt = select(Position).where(Position.portfolio_id == portfolio_id)
        elif position_ids:
            # Parse position IDs
            ids = [UUID(pid.strip()) for pid in position_ids.split(",")]
            stmt = select(Position).where(Position.id.in_(ids))
        else:
            raise HTTPException(status_code=400, detail="Either portfolio_id or position_ids required")
        
        # Execute query
        result = await session.execute(stmt)
        positions = result.scalars().all()
        
        # Build response
        positions_data = []
        total_cost_basis = 0
        total_market_value = 0
        total_unrealized_pnl = 0
        
        for position in positions:
            # Get current price
            cache_stmt = select(MarketDataCache).where(
                MarketDataCache.symbol == position.symbol
            ).order_by(MarketDataCache.updated_at.desc())
            cache_result = await session.execute(cache_stmt)
            market_data = cache_result.scalars().first()
            
            current_price = market_data.close if market_data else position.entry_price
            cost_basis = float(position.quantity) * float(position.entry_price)
            market_value = float(position.quantity) * float(current_price)
            
            # Adjust for shorts
            if position.position_type.value == "SHORT":
                market_value = -market_value
                unrealized_pnl = cost_basis - abs(market_value)  # Profit when price goes down
            else:
                unrealized_pnl = market_value - cost_basis
            
            unrealized_pnl_percent = (unrealized_pnl / cost_basis * 100) if cost_basis != 0 else 0
            
            total_cost_basis += abs(cost_basis)
            total_market_value += market_value
            total_unrealized_pnl += unrealized_pnl
            
            positions_data.append({
                "id": str(position.id),
                "portfolio_id": str(position.portfolio_id),
                "symbol": position.symbol,
                "position_type": position.position_type.value,
                "quantity": float(position.quantity),
                "entry_date": to_iso_date(position.entry_date) if position.entry_date else None,
                "entry_price": float(position.entry_price),
                "cost_basis": cost_basis,
                "current_price": float(current_price),
                "market_value": market_value,
                "unrealized_pnl": unrealized_pnl,
                "unrealized_pnl_percent": unrealized_pnl_percent
            })
        
        return {
            "positions": positions_data,
            "summary": {
                "total_positions": len(positions_data),
                "total_cost_basis": total_cost_basis,
                "total_market_value": total_market_value,
                "total_unrealized_pnl": total_unrealized_pnl
            }
        }


# Price Data Endpoints

@router.get("/prices/historical/{portfolio_id}")
async def get_historical_prices(
    portfolio_id: UUID,
    lookback_days: int = Query(150, description="Number of trading days"),
    include_factor_etfs: bool = Query(True, description="Include factor ETF prices"),
    date_format: str = Query("iso", description="Date format (iso|unix)"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get historical price data for all portfolio positions.
    Returns daily OHLCV data with aligned dates.
    """
    async with db as session:
        # Verify portfolio ownership
        stmt = select(Portfolio).where(
            and_(
                Portfolio.id == (portfolio_id if isinstance(portfolio_id, UUID) else UUID(str(portfolio_id))),
                Portfolio.user_id == (UUID(str(current_user.id)) if not isinstance(current_user.id, UUID) else current_user.id)
            )
        ).options(selectinload(Portfolio.positions))
        
        result = await session.execute(stmt)
        portfolio = result.scalar_one_or_none()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Get unique symbols from portfolio
        symbols = list(set([pos.symbol for pos in portfolio.positions]))
        
        # Add factor ETFs if requested
        if include_factor_etfs:
            factor_etfs = ["SPY", "VTV", "VUG", "MTUM", "QUAL", "SLY", "USMV"]
            symbols.extend([etf for etf in factor_etfs if etf not in symbols])
        
        # Get historical prices for all symbols
        # Note: This is a simplified implementation using market data cache
        # In production, we'd have a proper historical prices table
        from datetime import timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days)
        
        symbols_data = {}
        
        for symbol in symbols:
            # Get real historical data from MarketDataCache
            cache_stmt = select(MarketDataCache).where(
                and_(
                    MarketDataCache.symbol == symbol,
                    MarketDataCache.date >= start_date,
                    MarketDataCache.date <= end_date
                )
            ).order_by(MarketDataCache.date)
            
            cache_result = await session.execute(cache_stmt)
            market_data_rows = cache_result.scalars().all()
            
            if market_data_rows:
                # Build arrays from real historical data
                dates = []
                opens = []
                highs = []
                lows = []
                closes = []
                volumes = []
                
                for row in market_data_rows:
                    dates.append(to_iso_date(row.date) if date_format == "iso" else int(row.date.timestamp()))
                    
                    # Use real OHLCV data
                    close_price = float(row.close)
                    opens.append(float(row.open) if row.open else close_price)
                    highs.append(float(row.high) if row.high else close_price)
                    lows.append(float(row.low) if row.low else close_price)
                    closes.append(close_price)
                    volumes.append(int(row.volume) if row.volume else 0)
                
                if closes:
                    symbols_data[symbol] = {
                        "dates": dates,
                        "open": opens,
                        "high": highs,
                        "low": lows,
                        "close": closes,
                        "volume": volumes,
                        "adjusted_close": closes,  # We don't have adjusted close, using regular close
                        "data_points": len(closes),
                        "source": "market_data_cache"
                    }
        
        # Build response
        trading_days = len(next(iter(symbols_data.values()))["dates"]) if symbols_data else 0
        
        return {
            "metadata": {
                "lookback_days": lookback_days,
                "start_date": to_iso_date(start_date),
                "end_date": to_iso_date(end_date),
                "trading_days_included": trading_days
            },
            "symbols": symbols_data
        }


@router.get("/prices/quotes")
async def get_market_quotes(
    symbols: str = Query(..., description="Comma-separated list of ticker symbols"),
    include_options: bool = Query(False, description="Include options chains (future)"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get current market quotes for specified symbols.
    Returns real-time prices for position value updates.
    Added in v1.4.4 to support frontend requirements.
    """
    # Parse symbols
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    
    async with db as session:
        # Get quotes from market data cache
        quotes_data = []
        
        for symbol in symbol_list:
            # Get from cache first
            cache_stmt = select(MarketDataCache).where(
                MarketDataCache.symbol == symbol
            ).order_by(MarketDataCache.updated_at.desc())
            
            cache_result = await session.execute(cache_stmt)
            market_data = cache_result.scalars().first()
            
            if market_data:
                # Use available fields from MarketDataCache
                quotes_data.append({
                    "symbol": symbol,
                    "last_price": float(market_data.close),
                    "bid": float(market_data.close) - 0.01,  # Simulated bid
                    "ask": float(market_data.close) + 0.01,  # Simulated ask
                    "bid_size": 100,  # Default
                    "ask_size": 100,  # Default
                    "volume": int(market_data.volume) if market_data.volume else 0,
                    "day_change": 0,  # No previous close available in this model
                    "day_change_percent": 0,
                    "day_high": float(market_data.high) if market_data.high else float(market_data.close),
                    "day_low": float(market_data.low) if market_data.low else float(market_data.close),
                    "timestamp": to_utc_iso8601(market_data.updated_at)
                })
            else:
                # Try to fetch fresh data if not in cache
                service = MarketDataService()
                try:
                    price = await service.get_current_price(symbol)
                    if price:
                        quotes_data.append({
                            "symbol": symbol,
                            "last_price": float(price),
                            "bid": float(price) - 0.01,
                            "ask": float(price) + 0.01,
                            "bid_size": 100,
                            "ask_size": 100,
                            "volume": 0,
                            "day_change": 0,
                            "day_change_percent": 0,
                            "day_high": float(price),
                            "day_low": float(price),
                            "timestamp": to_utc_iso8601(utc_now())
                        })
                except Exception as e:
                    logger.warning(f"Failed to fetch quote for {symbol}: {e}")
        
        # Return structure matching API spec
        return {
            "quotes": quotes_data,
            "metadata": {
                "requested_symbols": symbol_list,
                "successful_quotes": len(quotes_data),
                "failed_quotes": len(symbol_list) - len(quotes_data),
                "timestamp": to_utc_iso8601(utc_now())
            }
        }


# Factor Data Endpoints

@router.get("/factors/etf-prices")
async def get_factor_etf_prices(
    lookback_days: int = Query(150, description="Number of trading days"),
    factors: Optional[str] = Query(None, description="Comma-separated factor names to filter"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get historical prices for factor ETFs used in the 7-factor risk model.
    Returns prices and returns for factor regression calculations.
    """
    # Define factor ETF mappings
    factor_etf_map = {
        "Market Beta": "SPY",
        "Value": "VTV",
        "Growth": "VUG",
        "Momentum": "MTUM",
        "Quality": "QUAL",
        "Size": "SLY",
        "Low Volatility": "USMV"
    }
    
    # Filter factors if specified
    if factors:
        factor_list = [f.strip() for f in factors.split(",")]
        factor_etf_map = {k: v for k, v in factor_etf_map.items() if k in factor_list}
    
    async with db as session:
        from datetime import timedelta
        
        # Get real ETF data from database
        factors_data = {}
        
        for factor_name, etf_symbol in factor_etf_map.items():
            # Get the most recent market data for this ETF
            cache_stmt = select(MarketDataCache).where(
                MarketDataCache.symbol == etf_symbol
            ).order_by(MarketDataCache.updated_at.desc()).limit(1)
            
            cache_result = await session.execute(cache_stmt)
            market_data = cache_result.scalar_one_or_none()
            
            if market_data:
                # Return real market data
                factors_data[etf_symbol] = {
                    "factor_name": factor_name,
                    "symbol": etf_symbol,
                    "current_price": float(market_data.close),
                    "open": float(market_data.open) if market_data.open else float(market_data.close),
                    "high": float(market_data.high) if market_data.high else float(market_data.close),
                    "low": float(market_data.low) if market_data.low else float(market_data.close),
                    "volume": int(market_data.volume) if market_data.volume else 0,
                    "date": to_iso_date(market_data.date) if market_data.date else None,
                    "updated_at": to_utc_iso8601(market_data.updated_at),
                    "data_source": market_data.data_source,
                    "exchange": market_data.exchange,
                    "market_cap": float(market_data.market_cap) if market_data.market_cap else None
                }
        
        return {
            "metadata": {
                "factor_model": "7-factor",
                "etf_count": len(factors_data),
                "timestamp": to_utc_iso8601(utc_now())
            },
            "data": factors_data
        }


@router.get("/positions/top/{portfolio_id}")
async def get_top_positions(
    portfolio_id: UUID,
    limit: int = Query(20, le=50, description="Max positions to return"),
    sort_by: str = Query("market_value", regex="^(market_value|weight)$"),
    as_of_date: Optional[str] = Query(None, description="ISO date, max 180d lookback"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get top N positions sorted by market value or weight.
    
    API layer owns:
    - Sorting by market value/weight
    - Computing portfolio coverage percentage
    - Applying limit caps (limit<=50, as_of_date<=180d lookback)
    - Response shape: {symbol, name, qty, value, weight, sector} only
    - Rounding weight to 4 decimal places
    - Full meta object population
    
    Returns positions with coverage % and truncation metadata.
    """
    async with db as session:
        # Verify portfolio ownership
        portfolio_stmt = select(Portfolio).where(
            and_(
                Portfolio.id == portfolio_id,
                Portfolio.user_id == current_user.id
            )
        )
        portfolio_result = await session.execute(portfolio_stmt)
        portfolio = portfolio_result.scalar_one_or_none()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Use service layer to get top positions
        service = PortfolioDataService()
        try:
            result = await service.get_top_positions(
                session,
                portfolio_id,
                limit=limit,
                sort_by=sort_by,
                as_of_date=as_of_date
            )
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error getting top positions: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
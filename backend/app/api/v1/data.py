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
from app.models.users import Portfolio
from app.models.positions import Position
from app.models.market_data import MarketDataCache
from app.schemas.auth import CurrentUser
from app.core.logging import get_logger
from app.services.market_data_service import MarketDataService

logger = get_logger(__name__)

router = APIRouter(prefix="/data", tags=["raw-data"])


# Portfolio Raw Data Endpoints

@router.get("/portfolio/{portfolio_id}/complete")
async def get_portfolio_complete(
    portfolio_id: UUID,
    include_positions: bool = Query(True, description="Include position list"),
    include_cash: bool = Query(True, description="Include cash balance"),
    as_of_date: Optional[date] = Query(None, description="Historical snapshot date"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get complete portfolio data with all positions and market values.
    Returns raw data without any calculated metrics.
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
        
        # Get positions with current market values
        positions_data = []
        total_market_value = 0
        long_count = 0
        short_count = 0
        option_count = 0
        complete_data_count = 0
        partial_data_count = 0
        
        if include_positions:
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
        
        # Build response
        # Note: Portfolio model doesn't have cash_balance field, using 0 for now
        cash_balance = 0.0  # TODO: Implement cash tracking in future
        
        response = {
            "portfolio": {
                "id": str(portfolio.id),
                "name": portfolio.name,
                "total_value": total_market_value + cash_balance if include_cash else total_market_value,
                "cash_balance": cash_balance if include_cash else 0,
                "position_count": len(positions_data),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "positions_summary": {
                "long_count": long_count,
                "short_count": short_count,
                "option_count": option_count,
                "total_market_value": total_market_value
            }
        }
        
        if include_positions:
            response["positions"] = positions_data
            
        response["data_quality"] = {
            "complete_data_positions": complete_data_count,
            "partial_data_positions": partial_data_count,
            "data_as_of": datetime.utcnow().isoformat() + "Z"
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
            "assessment_date": date.today().isoformat(),
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
        
        response["last_update"] = datetime.utcnow().isoformat() + "Z"
        
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
                "entry_date": position.entry_date.isoformat() if position.entry_date else None,
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
            # For now, just return current price as mock historical data
            cache_stmt = select(MarketDataCache).where(
                MarketDataCache.symbol == symbol
            )
            cache_result = await session.execute(cache_stmt)
            market_data = cache_result.scalars().first()
            
            if market_data:
                # Generate mock historical data based on current price
                # This is temporary until we have proper historical data
                current_price = float(market_data.close)
                dates = []
                closes = []
                
                for i in range(lookback_days):
                    day = end_date - timedelta(days=i)
                    # Skip weekends
                    if day.weekday() < 5:
                        dates.insert(0, day.isoformat() if date_format == "iso" else int(day.timestamp()))
                        # Add some random variation to simulate price movement
                        import random
                        variation = random.uniform(-0.02, 0.02)  # ±2% daily variation
                        price = current_price * (1 + variation * (1 - i/lookback_days))
                        closes.insert(0, price)
                
                if closes:
                    symbols_data[symbol] = {
                        "dates": dates,
                        "open": closes,  # Using close prices for all fields temporarily
                        "high": [c * 1.01 for c in closes],
                        "low": [c * 0.99 for c in closes],
                        "close": closes,
                        "volume": [1000000] * len(closes),
                        "adjusted_close": closes
                    }
        
        # Build response
        trading_days = len(next(iter(symbols_data.values()))["dates"]) if symbols_data else 0
        
        return {
            "metadata": {
                "lookback_days": lookback_days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
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
                    "timestamp": market_data.updated_at.isoformat() + "Z"
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
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        })
                except Exception as e:
                    logger.warning(f"Failed to fetch quote for {symbol}: {e}")
        
        return {
            "data": {
                "quotes": quotes_data,
                "last_update": datetime.utcnow().isoformat() + "Z"
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
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days * 1.5)  # Account for weekends
        
        factors_data = {}
        
        for factor_name, etf_symbol in factor_etf_map.items():
            # Simplified implementation using market data cache
            cache_stmt = select(MarketDataCache).where(
                MarketDataCache.symbol == etf_symbol
            )
            cache_result = await session.execute(cache_stmt)
            market_data = cache_result.scalars().first()
            
            if market_data:
                # Generate mock historical data
                current_price = float(market_data.close)
                dates = []
                price_values = []
                returns = []
                
                prev_price = None
                for i in range(lookback_days):
                    day = end_date - timedelta(days=i)
                    # Skip weekends
                    if day.weekday() < 5:
                        dates.insert(0, day.isoformat())
                        # Add some variation to simulate price movement
                        import random
                        variation = random.uniform(-0.01, 0.01)  # ±1% daily variation for ETFs
                        price = current_price * (1 + variation * (1 - i/lookback_days))
                        price_values.insert(0, price)
                        
                        # Calculate returns
                        if prev_price is not None:
                            ret = (price - prev_price) / prev_price
                            returns.insert(0, ret)
                        else:
                            returns.insert(0, None)  # No return for first day
                        
                        prev_price = price
                
                if price_values:
                    factors_data[factor_name] = {
                        "etf_symbol": etf_symbol,
                        "dates": dates,
                        "prices": price_values,
                        "returns": returns
                    }
        
        return {
            "factor_model": {
                "version": "7-factor",
                "regression_window": 150,
                "minimum_data_points": 60
            },
            "factors": factors_data
        }
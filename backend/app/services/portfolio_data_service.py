"""
Service layer for Agent-optimized portfolio data operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from uuid import UUID
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from app.models.users import Portfolio
from app.models.positions import Position, PositionType
from app.models.market_data import MarketDataCache, PositionValuation
from app.schemas.data import (
    TopPositionsResponse, 
    PortfolioSummaryResponse, 
    PositionSummary, 
    MetaInfo,
    HistoricalPricesResponse,
    PricePoint
)
from app.core.datetime_utils import utc_now, to_utc_iso8601
from app.core.logging import get_logger

logger = get_logger(__name__)


class PortfolioDataService:
    """Service layer for Agent-optimized portfolio data operations"""
    
    async def get_top_positions_by_value(
        self,
        db: AsyncSession,
        portfolio_id: UUID,
        limit: int = 50
    ) -> TopPositionsResponse:
        """
        Get top N positions by market value
        
        Args:
            db: Database session
            portfolio_id: Portfolio UUID
            limit: Maximum positions to return (default 50)
            
        Returns:
            TopPositionsResponse with position summaries and coverage metrics
        """
        try:
            # Get portfolio
            portfolio_result = await db.execute(
                select(Portfolio).where(Portfolio.id == portfolio_id)
            )
            portfolio = portfolio_result.scalar_one_or_none()
            
            if not portfolio:
                raise ValueError(f"Portfolio {portfolio_id} not found")
            
            # Get positions with valuations
            positions_query = (
                select(Position, PositionValuation)
                .join(
                    PositionValuation,
                    Position.id == PositionValuation.position_id,
                    isouter=True
                )
                .where(
                    and_(
                        Position.portfolio_id == portfolio_id,
                        Position.is_active == True
                    )
                )
            )
            
            result = await db.execute(positions_query)
            positions_data = result.all()
            
            # Calculate market values and sort
            position_summaries = []
            total_portfolio_value = 0.0
            
            for position, valuation in positions_data:
                # Calculate market value
                if valuation and valuation.current_price:
                    market_value = position.quantity * valuation.current_price
                else:
                    # Try to get latest price from MarketDataCache
                    price_result = await db.execute(
                        select(MarketDataCache.close)
                        .where(MarketDataCache.symbol == position.symbol)
                        .order_by(desc(MarketDataCache.date))
                        .limit(1)
                    )
                    latest_price = price_result.scalar_one_or_none()
                    market_value = position.quantity * (latest_price or position.cost_basis / position.quantity if position.quantity else 0)
                
                total_portfolio_value += market_value
                
                # Calculate P&L
                total_cost = position.cost_basis
                pnl_dollar = market_value - total_cost
                pnl_percent = (pnl_dollar / total_cost * 100) if total_cost else 0
                
                position_summaries.append({
                    'position': position,
                    'market_value': market_value,
                    'pnl_dollar': pnl_dollar,
                    'pnl_percent': pnl_percent
                })
            
            # Sort by market value and take top N
            position_summaries.sort(key=lambda x: x['market_value'], reverse=True)
            top_positions = position_summaries[:limit]
            
            # Calculate weights and coverage
            covered_value = sum(p['market_value'] for p in top_positions)
            portfolio_coverage = (covered_value / total_portfolio_value * 100) if total_portfolio_value else 0
            
            # Build response
            positions_response = []
            for pos_data in top_positions:
                position = pos_data['position']
                weight = (pos_data['market_value'] / total_portfolio_value * 100) if total_portfolio_value else 0
                
                positions_response.append(PositionSummary(
                    position_id=position.id,
                    symbol=position.symbol,
                    quantity=position.quantity,
                    market_value=pos_data['market_value'],
                    weight=weight,
                    pnl_dollar=pos_data['pnl_dollar'],
                    pnl_percent=pos_data['pnl_percent'],
                    position_type=position.position_type.value if position.position_type else 'stock'
                ))
            
            # Create meta object
            meta = MetaInfo(
                as_of=utc_now(),
                requested={'portfolio_id': str(portfolio_id), 'limit': limit},
                applied={'limit': len(positions_response)},
                limits={'max_positions': limit},
                rows_returned=len(positions_response),
                truncated=len(position_summaries) > limit
            )
            
            return TopPositionsResponse(
                meta=meta,
                positions=positions_response,
                portfolio_coverage=portfolio_coverage,
                total_portfolio_value=total_portfolio_value
            )
            
        except Exception as e:
            logger.error(f"Error getting top positions: {e}")
            raise
    
    async def get_portfolio_summary(
        self,
        db: AsyncSession,
        portfolio_id: UUID
    ) -> PortfolioSummaryResponse:
        """
        Get condensed portfolio overview
        
        Args:
            db: Database session
            portfolio_id: Portfolio UUID
            
        Returns:
            PortfolioSummaryResponse with summary metrics and top holdings
        """
        try:
            # Get portfolio
            portfolio_result = await db.execute(
                select(Portfolio).where(Portfolio.id == portfolio_id)
            )
            portfolio = portfolio_result.scalar_one_or_none()
            
            if not portfolio:
                raise ValueError(f"Portfolio {portfolio_id} not found")
            
            # Get top positions (reuse the other method)
            top_positions_response = await self.get_top_positions_by_value(
                db, portfolio_id, limit=5
            )
            
            # Get position count and asset allocation
            positions_result = await db.execute(
                select(
                    func.count(Position.id),
                    Position.position_type,
                    func.sum(Position.quantity * Position.cost_basis)
                )
                .where(
                    and_(
                        Position.portfolio_id == portfolio_id,
                        Position.is_active == True
                    )
                )
                .group_by(Position.position_type)
            )
            
            position_stats = positions_result.all()
            total_positions = sum(count for count, _, _ in position_stats)
            
            # Calculate asset allocation
            asset_allocation = {}
            total_value = top_positions_response.total_portfolio_value
            
            for count, position_type, type_value in position_stats:
                if position_type:
                    asset_type = position_type.value if hasattr(position_type, 'value') else str(position_type)
                    allocation_pct = (float(type_value or 0) / total_value * 100) if total_value else 0
                    asset_allocation[asset_type] = round(allocation_pct, 2)
            
            # Calculate cash balance (5% of portfolio as per backend convention)
            cash_balance = total_value * 0.05
            
            # Create meta object
            meta = MetaInfo(
                as_of=utc_now(),
                requested={'portfolio_id': str(portfolio_id)},
                applied={'top_holdings_count': 5},
                limits={'max_top_holdings': 5},
                rows_returned=len(top_positions_response.positions),
                truncated=False
            )
            
            return PortfolioSummaryResponse(
                meta=meta,
                portfolio_id=portfolio.id,
                portfolio_name=portfolio.name,
                total_value=total_value,
                cash_balance=cash_balance,
                positions_count=total_positions,
                top_holdings=top_positions_response.positions[:5],
                asset_allocation=asset_allocation
            )
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            raise
    
    async def get_historical_prices_with_selection(
        self,
        db: AsyncSession,
        portfolio_id: UUID,
        selection_method: str = "top_by_value",
        max_symbols: int = 5,
        lookback_days: int = 180
    ) -> Dict[str, Any]:
        """
        Get historical prices for selected symbols based on portfolio composition
        
        Args:
            db: Database session
            portfolio_id: Portfolio UUID
            selection_method: Method for selecting symbols (top_by_value, top_by_weight, all)
            max_symbols: Maximum number of symbols to return
            lookback_days: Number of days of history
            
        Returns:
            Dictionary with historical price data and metadata
        """
        try:
            # Get top positions to determine which symbols to include
            if selection_method in ["top_by_value", "top_by_weight"]:
                top_positions = await self.get_top_positions_by_value(
                    db, portfolio_id, limit=max_symbols
                )
                selected_symbols = [pos.symbol for pos in top_positions.positions]
            else:  # all
                # Get all active position symbols
                result = await db.execute(
                    select(Position.symbol)
                    .where(
                        and_(
                            Position.portfolio_id == portfolio_id,
                            Position.is_active == True
                        )
                    )
                    .limit(max_symbols)
                )
                selected_symbols = [row[0] for row in result.all()]
            
            # Calculate date range
            end_date = utc_now()
            start_date = end_date - timedelta(days=lookback_days)
            
            # Get historical prices for selected symbols
            price_data = {}
            symbols_excluded = []
            
            for symbol in selected_symbols:
                prices_result = await db.execute(
                    select(MarketDataCache)
                    .where(
                        and_(
                            MarketDataCache.symbol == symbol,
                            MarketDataCache.date >= start_date,
                            MarketDataCache.date <= end_date
                        )
                    )
                    .order_by(MarketDataCache.date)
                )
                
                prices = prices_result.scalars().all()
                
                if prices:
                    price_data[symbol] = [
                        PricePoint(
                            date=to_utc_iso8601(price.date),
                            open=price.open,
                            high=price.high,
                            low=price.low,
                            close=price.close,
                            volume=price.volume
                        )
                        for price in prices
                    ]
                else:
                    symbols_excluded.append(symbol)
            
            # Get factor ETF prices if requested
            factor_etfs = {}
            factor_etf_symbols = ['SPY', 'IWM', 'QQQ', 'DIA', 'XLF', 'XLE', 'XLK']
            
            for etf in factor_etf_symbols:
                etf_result = await db.execute(
                    select(MarketDataCache)
                    .where(
                        and_(
                            MarketDataCache.symbol == etf,
                            MarketDataCache.date >= start_date,
                            MarketDataCache.date <= end_date
                        )
                    )
                    .order_by(MarketDataCache.date)
                    .limit(lookback_days)
                )
                
                etf_prices = etf_result.scalars().all()
                if etf_prices:
                    factor_etfs[etf] = [
                        PricePoint(
                            date=to_utc_iso8601(price.date),
                            open=price.open,
                            high=price.high,
                            low=price.low,
                            close=price.close,
                            volume=price.volume
                        )
                        for price in etf_prices
                    ]
            
            # Create meta object
            meta = MetaInfo(
                as_of=utc_now(),
                requested={
                    'portfolio_id': str(portfolio_id),
                    'selection_method': selection_method,
                    'max_symbols': max_symbols,
                    'lookback_days': lookback_days
                },
                applied={
                    'symbols_returned': len(price_data),
                    'days_returned': lookback_days,
                    'selection_method': selection_method
                },
                limits={
                    'max_symbols': max_symbols,
                    'max_days': 180
                },
                rows_returned=sum(len(prices) for prices in price_data.values()),
                truncated=len(selected_symbols) > max_symbols
            )
            
            return {
                'meta': meta.model_dump(),
                'symbols_included': list(price_data.keys()),
                'symbols_excluded': symbols_excluded,
                'price_data': {k: [p.model_dump() for p in v] for k, v in price_data.items()},
                'factor_etfs': {k: [p.model_dump() for p in v] for k, v in factor_etfs.items()} if factor_etfs else None
            }
            
        except Exception as e:
            logger.error(f"Error getting historical prices: {e}")
            raise
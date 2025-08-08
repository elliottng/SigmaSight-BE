"""
Portfolio snapshot generation for daily portfolio state tracking
"""
import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.positions import Position, PositionType
from app.models.snapshots import PortfolioSnapshot
from app.models.market_data import PositionGreeks
from app.calculations.portfolio import (
    calculate_portfolio_exposures,
    aggregate_portfolio_greeks
)
from app.calculations.market_data import calculate_position_market_value
from app.utils.trading_calendar import trading_calendar

logger = logging.getLogger(__name__)


async def create_portfolio_snapshot(
    db: AsyncSession,
    portfolio_id: UUID,
    calculation_date: date
) -> Dict[str, Any]:
    """
    Generate a complete daily snapshot of portfolio state
    
    Args:
        db: Database session
        portfolio_id: UUID of the portfolio
        calculation_date: Date for the snapshot (typically today)
        
    Returns:
        Dictionary with snapshot creation results
    """
    logger.info(f"Creating portfolio snapshot for {portfolio_id} on {calculation_date}")
    
    try:
        # Check if it's a trading day
        if not trading_calendar.is_trading_day(calculation_date):
            logger.warning(f"{calculation_date} is not a trading day, skipping snapshot")
            return {
                "success": False,
                "message": f"{calculation_date} is not a trading day",
                "snapshot": None
            }
        
        # Step 1: Fetch all active positions
        active_positions = await _fetch_active_positions(db, portfolio_id, calculation_date)
        logger.info(f"Found {len(active_positions)} active positions")
        
        if not active_positions:
            logger.warning(f"No active positions found for portfolio {portfolio_id}")
            # Still create a zero snapshot
            snapshot = await _create_zero_snapshot(db, portfolio_id, calculation_date)
            return {
                "success": True,
                "message": "Created zero snapshot (no active positions)",
                "snapshot": snapshot
            }
        
        # Step 2: Calculate market values for all positions
        position_data = await _prepare_position_data(db, active_positions, calculation_date)
        
        # Step 3: Calculate portfolio aggregations
        aggregations = calculate_portfolio_exposures(position_data)
        
        # Step 4: Aggregate Greeks
        greeks = aggregate_portfolio_greeks(position_data)
        
        # Step 5: Calculate P&L
        pnl_data = await _calculate_pnl(db, portfolio_id, calculation_date, aggregations['gross_exposure'])
        
        # Step 6: Count position types
        position_counts = _count_positions(active_positions)
        
        # Step 7: Create or update snapshot
        snapshot = await _create_or_update_snapshot(
            db=db,
            portfolio_id=portfolio_id,
            calculation_date=calculation_date,
            aggregations=aggregations,
            greeks=greeks,
            pnl_data=pnl_data,
            position_counts=position_counts
        )
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Snapshot created successfully",
            "snapshot": snapshot,
            "statistics": {
                "positions_processed": len(active_positions),
                "total_value": float(aggregations['gross_exposure']),
                "daily_pnl": float(pnl_data['daily_pnl']),
                "warnings": position_data.get('warnings', [])
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating portfolio snapshot: {str(e)}")
        await db.rollback()
        return {
            "success": False,
            "message": f"Error creating snapshot: {str(e)}",
            "snapshot": None
        }


async def _fetch_active_positions(
    db: AsyncSession,
    portfolio_id: UUID,
    calculation_date: date
) -> List[Position]:
    """Fetch all active positions for a portfolio on a given date"""
    query = select(Position).where(
        and_(
            Position.portfolio_id == portfolio_id,
            Position.entry_date <= calculation_date,
            or_(
                Position.exit_date.is_(None),
                Position.exit_date > calculation_date
            ),
            Position.deleted_at.is_(None)
        )
    )
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def _prepare_position_data(
    db: AsyncSession,
    positions: List[Position],
    calculation_date: date
) -> Dict[str, Any]:
    """Prepare position data with market values and Greeks"""
    position_data = []
    warnings = []
    
    # Import needed for price lookup
    from app.models.market_data import MarketDataCache
    from sqlalchemy import select, and_
    
    for position in positions:
        try:
            # First, get the price for this position as of calculation_date
            price_query = select(MarketDataCache.close).where(
                and_(
                    MarketDataCache.symbol == position.symbol,
                    MarketDataCache.date <= calculation_date
                )
            ).order_by(MarketDataCache.date.desc()).limit(1)
            
            price_result = await db.execute(price_query)
            current_price = price_result.scalar_one_or_none()
            
            if current_price is None:
                warnings.append(f"No price data available for {position.symbol} as of {calculation_date}")
                continue
            
            # Calculate market value with correct function signature
            market_value_result = await calculate_position_market_value(
                position=position,
                current_price=Decimal(str(current_price))
            )
            
            # Fetch Greeks if available
            greeks_query = select(PositionGreeks).where(
                and_(
                    PositionGreeks.position_id == position.id,
                    PositionGreeks.calculation_date == calculation_date
                )
            )
            greeks_result = await db.execute(greeks_query)
            greeks_record = greeks_result.scalar_one_or_none()
            
            greeks = None
            if greeks_record:
                greeks = {
                    "delta": greeks_record.delta,
                    "gamma": greeks_record.gamma,
                    "theta": greeks_record.theta,
                    "vega": greeks_record.vega,
                    "rho": greeks_record.rho
                }
            elif _is_options_position(position):
                warnings.append(f"Missing Greeks for options position {position.symbol}")
            
            position_data.append({
                "id": position.id,
                "symbol": position.symbol,
                "quantity": position.quantity,
                "market_value": market_value_result["market_value"],  # Always positive
                "exposure": market_value_result["exposure"],          # Signed value (negative for shorts)
                "position_type": position.position_type,
                "greeks": greeks
            })
            
        except Exception as e:
            logger.error(f"Error processing position {position.id}: {str(e)}")
            warnings.append(f"Error processing position {position.symbol}: {str(e)}")
    
    return {
        "positions": position_data,
        "warnings": warnings
    }


async def _calculate_pnl(
    db: AsyncSession,
    portfolio_id: UUID,
    calculation_date: date,
    current_value: Decimal
) -> Dict[str, Decimal]:
    """Calculate daily and cumulative P&L"""
    # Get previous trading day
    previous_date = trading_calendar.get_previous_trading_day(calculation_date)
    
    if not previous_date:
        logger.warning("No previous trading day found, setting P&L to 0")
        return {
            "daily_pnl": Decimal('0'),
            "daily_return": Decimal('0'),
            "cumulative_pnl": Decimal('0')
        }
    
    # Fetch previous snapshot
    prev_query = select(PortfolioSnapshot).where(
        and_(
            PortfolioSnapshot.portfolio_id == portfolio_id,
            PortfolioSnapshot.snapshot_date == previous_date
        )
    )
    prev_result = await db.execute(prev_query)
    previous_snapshot = prev_result.scalar_one_or_none()
    
    if not previous_snapshot:
        logger.info("No previous snapshot found, this is the first snapshot")
        return {
            "daily_pnl": Decimal('0'),
            "daily_return": Decimal('0'),
            "cumulative_pnl": Decimal('0')
        }
    
    # Calculate daily P&L
    daily_pnl = current_value - previous_snapshot.total_value
    daily_return = (daily_pnl / previous_snapshot.total_value) if previous_snapshot.total_value != 0 else Decimal('0')
    
    # Calculate cumulative P&L (add today's P&L to previous cumulative)
    cumulative_pnl = (previous_snapshot.cumulative_pnl or Decimal('0')) + daily_pnl
    
    return {
        "daily_pnl": daily_pnl,
        "daily_return": daily_return,
        "cumulative_pnl": cumulative_pnl
    }


def _count_positions(positions: List[Position]) -> Dict[str, int]:
    """Count positions by type"""
    counts = {
        "total": len(positions),
        "long": 0,
        "short": 0
    }
    
    for position in positions:
        if position.quantity > 0:
            counts["long"] += 1
        else:
            counts["short"] += 1
    
    return counts


async def _create_or_update_snapshot(
    db: AsyncSession,
    portfolio_id: UUID,
    calculation_date: date,
    aggregations: Dict[str, Decimal],
    greeks: Dict[str, Decimal],
    pnl_data: Dict[str, Decimal],
    position_counts: Dict[str, int]
) -> PortfolioSnapshot:
    """Create or update portfolio snapshot"""
    
    # Check if snapshot already exists
    existing_query = select(PortfolioSnapshot).where(
        and_(
            PortfolioSnapshot.portfolio_id == portfolio_id,
            PortfolioSnapshot.snapshot_date == calculation_date
        )
    )
    existing_result = await db.execute(existing_query)
    existing_snapshot = existing_result.scalar_one_or_none()
    
    snapshot_data = {
        "portfolio_id": portfolio_id,
        "snapshot_date": calculation_date,
        "total_value": aggregations['gross_exposure'],
        "cash_value": Decimal('0'),  # Fully invested assumption
        "long_value": aggregations['long_exposure'],
        "short_value": aggregations['short_exposure'],
        "gross_exposure": aggregations['gross_exposure'],
        "net_exposure": aggregations['net_exposure'],
        "daily_pnl": pnl_data['daily_pnl'],
        "daily_return": pnl_data['daily_return'],
        "cumulative_pnl": pnl_data['cumulative_pnl'],
        "portfolio_delta": greeks['delta'],
        "portfolio_gamma": greeks['gamma'],
        "portfolio_theta": greeks['theta'],
        "portfolio_vega": greeks['vega'],
        "num_positions": position_counts['total'],
        "num_long_positions": position_counts['long'],
        "num_short_positions": position_counts['short']
    }
    
    if existing_snapshot:
        # Update existing snapshot
        for key, value in snapshot_data.items():
            setattr(existing_snapshot, key, value)
        snapshot = existing_snapshot
        logger.info(f"Updated existing snapshot for {calculation_date}")
    else:
        # Create new snapshot
        snapshot = PortfolioSnapshot(**snapshot_data)
        db.add(snapshot)
        logger.info(f"Created new snapshot for {calculation_date}")
    
    return snapshot


async def _create_zero_snapshot(
    db: AsyncSession,
    portfolio_id: UUID,
    calculation_date: date
) -> PortfolioSnapshot:
    """Create a snapshot with zero values when no positions exist"""
    zero_decimal = Decimal('0')
    
    snapshot = PortfolioSnapshot(
        portfolio_id=portfolio_id,
        snapshot_date=calculation_date,
        total_value=zero_decimal,
        cash_value=zero_decimal,
        long_value=zero_decimal,
        short_value=zero_decimal,
        gross_exposure=zero_decimal,
        net_exposure=zero_decimal,
        daily_pnl=zero_decimal,
        daily_return=zero_decimal,
        cumulative_pnl=zero_decimal,
        portfolio_delta=zero_decimal,
        portfolio_gamma=zero_decimal,
        portfolio_theta=zero_decimal,
        portfolio_vega=zero_decimal,
        num_positions=0,
        num_long_positions=0,
        num_short_positions=0
    )
    
    db.add(snapshot)
    await db.commit()
    
    return snapshot


def _is_options_position(position: Position) -> bool:
    """Check if position is an options position"""
    return position.position_type in [
        PositionType.LC, PositionType.LP, 
        PositionType.SC, PositionType.SP
    ]
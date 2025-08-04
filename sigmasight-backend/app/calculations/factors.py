"""
Factor Analysis Calculation Functions - Section 1.4.4
Implements 7-factor model with ETF proxies and regression analysis
"""
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID
import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import statsmodels.api as sm

from app.models.positions import Position
from app.models.market_data import MarketDataCache, PositionFactorExposure, FactorDefinition
from app.calculations.market_data import fetch_historical_prices
from app.constants.factors import (
    FACTOR_ETFS, REGRESSION_WINDOW_DAYS, MIN_REGRESSION_DAYS, 
    BETA_CAP_LIMIT, POSITION_CHUNK_SIZE, QUALITY_FLAG_FULL_HISTORY, 
    QUALITY_FLAG_LIMITED_HISTORY, OPTIONS_MULTIPLIER
)
from app.core.logging import get_logger

logger = get_logger(__name__)


async def fetch_factor_returns(
    db: AsyncSession,
    symbols: List[str],
    start_date: date,
    end_date: date
) -> pd.DataFrame:
    """
    Fetch factor returns calculated from ETF price changes
    
    Args:
        db: Database session
        symbols: List of factor ETF symbols (SPY, VTV, VUG, etc.)
        start_date: Start date for factor returns
        end_date: End date for factor returns
        
    Returns:
        DataFrame with dates as index and factor names as columns, containing daily returns
        
    Note:
        Returns are calculated as: (price_today - price_yesterday) / price_yesterday
        Missing data is handled by forward-filling and then dropping NaN rows
    """
    logger.info(f"Fetching factor returns for {len(symbols)} factors from {start_date} to {end_date}")
    
    if not symbols:
        logger.warning("Empty symbols list provided to fetch_factor_returns")
        return pd.DataFrame()
    
    # Fetch historical prices using existing function
    price_df = await fetch_historical_prices(
        db=db,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    
    if price_df.empty:
        logger.warning("No price data available for factor return calculations")
        return pd.DataFrame()
    
    # Calculate daily returns for each ETF
    returns_df = price_df.pct_change().dropna()
    
    # Map ETF symbols to factor names for cleaner output
    symbol_to_factor = {v: k for k, v in FACTOR_ETFS.items()}
    factor_columns = {}
    
    for symbol in returns_df.columns:
        if symbol in symbol_to_factor:
            factor_name = symbol_to_factor[symbol]
            factor_columns[symbol] = factor_name
        else:
            factor_columns[symbol] = symbol
    
    # Rename columns to factor names
    returns_df = returns_df.rename(columns=factor_columns)
    
    # Log data quality
    total_days = len(returns_df)
    missing_data = returns_df.isnull().sum()
    
    logger.info(f"Factor returns calculated: {total_days} days of data")
    if missing_data.any():
        logger.warning(f"Missing data in factor returns: {missing_data[missing_data > 0].to_dict()}")
    
    return returns_df


async def calculate_position_returns(
    db: AsyncSession,
    portfolio_id: UUID,
    start_date: date,
    end_date: date,
    use_delta_adjusted: bool = False
) -> pd.DataFrame:
    """
    Calculate exposure-based daily returns for portfolio positions
    
    Args:
        db: Database session
        portfolio_id: Portfolio ID to analyze
        start_date: Start date for return calculation
        end_date: End date for return calculation
        use_delta_adjusted: If True, use delta-adjusted exposure for options
        
    Returns:
        DataFrame with dates as index and position IDs as columns, containing daily returns
        
    Note:
        Returns are calculated based on position exposure changes:
        - Dollar exposure (default): quantity × price × multiplier
        - Delta-adjusted exposure: dollar_exposure × delta (for options)
    """
    logger.info(f"Calculating position returns for portfolio {portfolio_id}")
    logger.info(f"Date range: {start_date} to {end_date}, Delta-adjusted: {use_delta_adjusted}")
    
    # Get active positions for the portfolio
    stmt = select(Position).where(
        and_(
            Position.portfolio_id == portfolio_id,
            Position.exit_date.is_(None)  # Only active positions
        )
    )
    result = await db.execute(stmt)
    positions = result.scalars().all()
    
    if not positions:
        logger.warning(f"No active positions found for portfolio {portfolio_id}")
        return pd.DataFrame()
    
    # Get unique symbols for price fetching
    symbols = list(set(position.symbol for position in positions))
    logger.info(f"Found {len(positions)} positions with {len(symbols)} unique symbols")
    
    # Fetch historical prices for all symbols
    price_df = await fetch_historical_prices(
        db=db,
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    
    if price_df.empty:
        logger.warning("No price data available for position return calculations")
        return pd.DataFrame()
    
    # Calculate returns for each position
    position_returns = {}
    
    for position in positions:
        try:
            symbol = position.symbol.upper()
            
            if symbol not in price_df.columns:
                logger.warning(f"No price data for position {position.id} ({symbol})")
                continue
            
            # Get price series for this symbol
            prices = price_df[symbol].dropna()
            
            if len(prices) < 2:
                logger.warning(f"Insufficient price data for position {position.id} ({symbol})")
                continue
            
            # Calculate position multiplier
            multiplier = OPTIONS_MULTIPLIER if _is_options_position(position) else 1
            
            # Calculate base exposure time series
            base_exposure = prices * float(position.quantity) * multiplier
            
            # Apply delta adjustment if requested and position is options
            if use_delta_adjusted and _is_options_position(position):
                # For now, use a simplified delta calculation
                # TODO: Integrate with Greeks calculation from Section 1.4.2
                delta = await _get_position_delta(db, position)
                if delta is not None:
                    exposure = base_exposure * float(delta)
                else:
                    # Fallback to dollar exposure if delta unavailable
                    exposure = base_exposure
                    logger.warning(f"Delta unavailable for position {position.id}, using dollar exposure")
            else:
                exposure = base_exposure
            
            # Calculate daily returns from exposure changes
            returns = exposure.pct_change().dropna()
            
            if not returns.empty:
                position_returns[str(position.id)] = returns
                logger.debug(f"Calculated returns for position {position.id}: {len(returns)} days")
            
        except Exception as e:
            logger.error(f"Error calculating returns for position {position.id}: {str(e)}")
            continue
    
    if not position_returns:
        logger.warning("No position returns calculated")
        return pd.DataFrame()
    
    # Combine all position returns into a DataFrame
    returns_df = pd.DataFrame(position_returns)
    
    # Align dates and handle missing data
    returns_df = returns_df.fillna(0)  # Fill missing returns with 0
    
    logger.info(f"Position returns calculated: {len(returns_df)} days, {len(returns_df.columns)} positions")
    return returns_df


async def calculate_factor_betas_hybrid(
    db: AsyncSession,
    portfolio_id: UUID,
    calculation_date: date,
    use_delta_adjusted: bool = False
) -> Dict[str, Any]:
    """
    Calculate portfolio factor betas using 252-day regression analysis
    
    Args:
        db: Database session
        portfolio_id: Portfolio ID to analyze
        calculation_date: Date for the calculation (end of regression window)
        use_delta_adjusted: Use delta-adjusted exposures for options
        
    Returns:
        Dictionary containing:
        - factor_betas: Dict mapping factor names to beta values
        - position_betas: Dict mapping position IDs to their factor betas
        - data_quality: Dict with quality metrics
        - metadata: Calculation metadata
    """
    logger.info(f"Calculating factor betas for portfolio {portfolio_id} as of {calculation_date}")
    
    # Define regression window
    end_date = calculation_date
    start_date = end_date - timedelta(days=REGRESSION_WINDOW_DAYS + 30)  # Extra buffer for trading days
    
    try:
        # Step 1: Fetch factor returns
        factor_symbols = list(FACTOR_ETFS.values())
        factor_returns = await fetch_factor_returns(
            db=db,
            symbols=factor_symbols,
            start_date=start_date,
            end_date=end_date
        )
        
        if factor_returns.empty:
            raise ValueError("No factor returns data available")
        
        # Step 2: Fetch position returns
        position_returns = await calculate_position_returns(
            db=db,
            portfolio_id=portfolio_id,
            start_date=start_date,
            end_date=end_date,
            use_delta_adjusted=use_delta_adjusted
        )
        
        if position_returns.empty:
            raise ValueError("No position returns data available")
        
        # Step 3: Align data on common dates
        common_dates = factor_returns.index.intersection(position_returns.index)
        
        if len(common_dates) < MIN_REGRESSION_DAYS:
            logger.warning(f"Insufficient data: {len(common_dates)} days (minimum: {MIN_REGRESSION_DAYS})")
            quality_flag = QUALITY_FLAG_LIMITED_HISTORY
        else:
            quality_flag = QUALITY_FLAG_FULL_HISTORY
        
        # Align datasets
        factor_returns_aligned = factor_returns.loc[common_dates]
        position_returns_aligned = position_returns.loc[common_dates]
        
        # Step 4: Calculate factor betas for each position
        position_betas = {}
        regression_stats = {}
        
        for position_id in position_returns_aligned.columns:
            position_betas[position_id] = {}
            regression_stats[position_id] = {}
            
            try:
                y = position_returns_aligned[position_id].values
                
                # Run regression for each factor
                for factor_name in factor_returns_aligned.columns:
                    X = factor_returns_aligned[factor_name].values
                    
                    # Add constant for intercept
                    X_with_const = sm.add_constant(X)
                    
                    # Run OLS regression
                    model = sm.OLS(y, X_with_const).fit()
                    
                    # Extract beta (slope coefficient)
                    beta = model.params[1] if len(model.params) > 1 else 0.0
                    
                    # Cap beta at ±3 to prevent outliers
                    beta = max(-BETA_CAP_LIMIT, min(BETA_CAP_LIMIT, beta))
                    
                    position_betas[position_id][factor_name] = float(beta)
                    regression_stats[position_id][factor_name] = {
                        'r_squared': float(model.rsquared),
                        'p_value': float(model.pvalues[1]) if len(model.pvalues) > 1 else 1.0,
                        'std_err': float(model.bse[1]) if len(model.bse) > 1 else 0.0
                    }
                
            except Exception as e:
                logger.error(f"Error calculating betas for position {position_id}: {str(e)}")
                # Fill with zeros on error
                for factor_name in factor_returns_aligned.columns:
                    position_betas[position_id][factor_name] = 0.0
                    regression_stats[position_id][factor_name] = {
                        'r_squared': 0.0, 'p_value': 1.0, 'std_err': 0.0
                    }
        
        # Step 5: Calculate portfolio-level factor betas (exposure-weighted average)
        portfolio_betas = await _aggregate_portfolio_betas(
            db=db,
            portfolio_id=portfolio_id,
            position_betas=position_betas
        )
        
        # Step 6: Prepare results
        results = {
            'factor_betas': portfolio_betas,
            'position_betas': position_betas,
            'data_quality': {
                'quality_flag': quality_flag,
                'regression_days': len(common_dates),
                'required_days': MIN_REGRESSION_DAYS,
                'positions_processed': len(position_betas),
                'factors_processed': len(factor_returns_aligned.columns)
            },
            'metadata': {
                'calculation_date': calculation_date,
                'start_date': common_dates[0] if len(common_dates) > 0 else start_date,
                'end_date': common_dates[-1] if len(common_dates) > 0 else end_date,
                'use_delta_adjusted': use_delta_adjusted,
                'regression_window_days': REGRESSION_WINDOW_DAYS,
                'portfolio_id': str(portfolio_id)
            },
            'regression_stats': regression_stats
        }
        
        logger.info(f"Factor betas calculated successfully: {len(position_betas)} positions, {quality_flag}")
        return results
        
    except Exception as e:
        logger.error(f"Error in factor beta calculation: {str(e)}")
        raise


# Helper functions

def _is_options_position(position: Position) -> bool:
    """Check if position is an options position"""
    from app.models.positions import PositionType
    return position.position_type in [
        PositionType.LC, PositionType.LP, PositionType.SC, PositionType.SP
    ]


async def _get_position_delta(db: AsyncSession, position: Position) -> Optional[float]:
    """
    Get delta for options position from Greeks table
    TODO: Integrate with Section 1.4.2 Greeks calculations
    """
    if not _is_options_position(position):
        return 1.0 if position.quantity > 0 else -1.0
    
    # For now, return None to indicate delta unavailable
    # This will be integrated with Greeks calculations later
    return None


async def _aggregate_portfolio_betas(
    db: AsyncSession,
    portfolio_id: UUID,
    position_betas: Dict[str, Dict[str, float]]
) -> Dict[str, float]:
    """
    Aggregate position-level betas to portfolio level using exposure weighting
    """
    # Get current position exposures for weighting
    stmt = select(Position).where(
        and_(
            Position.portfolio_id == portfolio_id,
            Position.exit_date.is_(None)
        )
    )
    result = await db.execute(stmt)
    positions = result.scalars().all()
    
    if not positions:
        return {}
    
    # Calculate exposure weights
    total_exposure = Decimal('0')
    position_weights = {}
    
    for position in positions:
        # Simple exposure calculation for weighting
        multiplier = OPTIONS_MULTIPLIER if _is_options_position(position) else 1
        exposure = abs(position.quantity * (position.last_price or position.entry_price) * multiplier)
        total_exposure += exposure
        position_weights[str(position.id)] = exposure
    
    if total_exposure == 0:
        logger.warning("Total portfolio exposure is zero, using equal weights")
        equal_weight = 1.0 / len(positions)
        position_weights = {str(p.id): equal_weight for p in positions}
        total_exposure = Decimal('1')
    
    # Normalize weights
    for pos_id in position_weights:
        position_weights[pos_id] = float(position_weights[pos_id] / total_exposure)
    
    # Calculate weighted average betas
    portfolio_betas = {}
    
    # Get all factor names
    factor_names = set()
    for pos_betas in position_betas.values():
        factor_names.update(pos_betas.keys())
    
    for factor_name in factor_names:
        weighted_beta = 0.0
        
        for pos_id, weight in position_weights.items():
            if pos_id in position_betas and factor_name in position_betas[pos_id]:
                weighted_beta += position_betas[pos_id][factor_name] * weight
        
        portfolio_betas[factor_name] = weighted_beta
    
    return portfolio_betas


async def store_position_factor_exposures(
    db: AsyncSession,
    position_betas: Dict[str, Dict[str, float]],
    calculation_date: date,
    quality_flag: str = QUALITY_FLAG_FULL_HISTORY
) -> Dict[str, Any]:
    """
    Store position-level factor exposures in the database
    
    Args:
        db: Database session
        position_betas: Dictionary mapping position IDs to factor betas
        calculation_date: Date of the calculation
        quality_flag: Data quality indicator
        
    Returns:
        Dictionary with storage statistics
    """
    logger.info(f"Storing position factor exposures for {len(position_betas)} positions")
    
    results = {
        "positions_processed": 0,
        "records_stored": 0,
        "errors": []
    }
    
    try:
        # Get factor definitions for ID mapping
        stmt = select(FactorDefinition).where(FactorDefinition.is_active == True)
        result = await db.execute(stmt)
        factor_definitions = result.scalars().all()
        
        factor_name_to_id = {fd.name: fd.id for fd in factor_definitions}
        
        for position_id_str, factor_betas in position_betas.items():
            try:
                position_id = UUID(position_id_str)
                results["positions_processed"] += 1
                
                for factor_name, beta_value in factor_betas.items():
                    if factor_name not in factor_name_to_id:
                        logger.warning(f"Factor '{factor_name}' not found in database")
                        continue
                    
                    factor_id = factor_name_to_id[factor_name]
                    
                    # Create or update position factor exposure record
                    exposure_record = PositionFactorExposure(
                        position_id=position_id,
                        factor_id=factor_id,
                        calculation_date=calculation_date,
                        exposure_value=Decimal(str(beta_value)),
                        quality_flag=quality_flag
                    )
                    
                    # Use merge to handle upserts
                    db.add(exposure_record)
                    results["records_stored"] += 1
                
            except Exception as e:
                error_msg = f"Error storing exposures for position {position_id_str}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # Commit all changes
        await db.commit()
        logger.info(f"Stored {results['records_stored']} factor exposure records")
        
    except Exception as e:
        logger.error(f"Error in store_position_factor_exposures: {str(e)}")
        await db.rollback()
        results["errors"].append(f"Storage failed: {str(e)}")
        raise
    
    return results


async def aggregate_portfolio_factor_exposures(
    db: AsyncSession,
    position_betas: Dict[str, Dict[str, float]],
    portfolio_exposures: Dict[str, Any],
    portfolio_id: UUID,
    calculation_date: date
) -> Dict[str, Any]:
    """
    Aggregate position-level factor exposures to portfolio level and store
    
    Args:
        db: Database session
        position_betas: Position-level factor betas
        portfolio_exposures: Current portfolio exposures for weighting
        portfolio_id: Portfolio ID
        calculation_date: Date of calculation
        
    Returns:
        Dictionary with aggregation results
    """
    logger.info(f"Aggregating portfolio factor exposures for portfolio {portfolio_id}")
    
    try:
        # Calculate portfolio-level betas (reuse existing function)
        portfolio_betas = await _aggregate_portfolio_betas(
            db=db,
            portfolio_id=portfolio_id,
            position_betas=position_betas
        )
        
        # Get factor definitions
        stmt = select(FactorDefinition).where(FactorDefinition.is_active == True)
        result = await db.execute(stmt)
        factor_definitions = result.scalars().all()
        
        factor_name_to_id = {fd.name: fd.id for fd in factor_definitions}
        
        # Store portfolio-level factor exposures
        from app.models.market_data import FactorExposure
        
        records_stored = 0
        for factor_name, beta_value in portfolio_betas.items():
            if factor_name not in factor_name_to_id:
                logger.warning(f"Factor '{factor_name}' not found in database")
                continue
            
            factor_id = factor_name_to_id[factor_name]
            
            # Calculate dollar exposure (beta * portfolio value)
            portfolio_value = portfolio_exposures.get("gross_exposure", Decimal('0'))
            exposure_dollar = float(beta_value) * float(portfolio_value) if portfolio_value else None
            
            # Create portfolio factor exposure record
            exposure_record = FactorExposure(
                portfolio_id=portfolio_id,
                factor_id=factor_id,
                calculation_date=calculation_date,
                exposure_value=Decimal(str(beta_value)),
                exposure_dollar=Decimal(str(exposure_dollar)) if exposure_dollar else None
            )
            
            db.add(exposure_record)
            records_stored += 1
        
        await db.commit()
        
        results = {
            "success": True,
            "portfolio_betas": portfolio_betas,
            "records_stored": records_stored,
            "calculation_date": calculation_date,
            "portfolio_id": str(portfolio_id)
        }
        
        logger.info(f"Portfolio factor exposures aggregated and stored: {records_stored} records")
        return results
        
    except Exception as e:
        logger.error(f"Error in aggregate_portfolio_factor_exposures: {str(e)}")
        await db.rollback()
        raise
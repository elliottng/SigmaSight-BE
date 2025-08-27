"""
Data Quality Monitoring for Batch Processing - Section 4.7
Provides pre-flight validation and quality scoring for batch operations
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.logging import get_logger
from app.models.positions import Position
from app.models.market_data import MarketDataCache
from app.models.users import Portfolio
from app.core.datetime_utils import utc_now

logger = get_logger(__name__)


class DataQualityValidator:
    """
    Validates data quality before and during batch processing operations
    """
    
    def __init__(self):
        self.quality_thresholds = {
            'minimum_coverage': 0.90,  # 90% of symbols must have data
            'data_freshness_hours': 48,  # Data must be within 48 hours
            'minimum_historical_days': 30  # At least 30 days of historical data
        }
    
    async def validate_data_coverage(
        self,
        db: AsyncSession,
        portfolio_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate data coverage for portfolio positions
        
        Args:
            db: Database session
            portfolio_id: Optional portfolio to validate (if None, validates all)
            
        Returns:
            Dictionary with validation results and quality scores
        """
        logger.info(f"Starting data coverage validation for portfolio: {portfolio_id or 'ALL'}")
        
        try:
            # Get positions to validate
            positions = await self._get_positions_for_validation(db, portfolio_id)
            
            if not positions:
                logger.warning(f"No positions found for validation")
                return {
                    'status': 'warning',
                    'message': 'No positions to validate',
                    'quality_score': 0.0,
                    'coverage_details': {}
                }
            
            # Get unique symbols
            symbols = list(set(pos.symbol for pos in positions))
            logger.info(f"Validating data coverage for {len(symbols)} unique symbols")
            
            # Check current price data availability
            current_data_coverage = await self._check_current_price_coverage(db, symbols)
            
            # Check historical data availability
            historical_data_coverage = await self._check_historical_data_coverage(db, symbols)
            
            # Check data freshness
            freshness_results = await self._check_data_freshness(db, symbols)
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(
                current_data_coverage,
                historical_data_coverage,
                freshness_results
            )
            
            # Determine status
            status = 'passed' if quality_score >= self.quality_thresholds['minimum_coverage'] else 'failed'
            
            result = {
                'status': status,
                'quality_score': quality_score,
                'total_symbols': len(symbols),
                'validation_timestamp': datetime.utcnow(),
                'coverage_details': {
                    'current_prices': current_data_coverage,
                    'historical_data': historical_data_coverage,
                    'data_freshness': freshness_results
                },
                'thresholds': self.quality_thresholds,
                'recommendations': self._generate_recommendations(
                    current_data_coverage,
                    historical_data_coverage,
                    freshness_results
                )
            }
            
            logger.info(
                f"Data coverage validation complete: {status.upper()} "
                f"(score: {quality_score:.2%})"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Data coverage validation failed: {str(e)}")
            return {
                'status': 'error',
                'message': f"Validation failed: {str(e)}",
                'quality_score': 0.0,
                'validation_timestamp': datetime.utcnow()
            }
    
    async def _get_positions_for_validation(
        self,
        db: AsyncSession,
        portfolio_id: Optional[str]
    ) -> List[Position]:
        """Get positions to validate based on portfolio filter"""
        
        if portfolio_id:
            # Validate specific portfolio
            stmt = select(Position).where(Position.portfolio_id == portfolio_id)
        else:
            # Validate all active positions
            stmt = select(Position)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    async def _check_current_price_coverage(
        self,
        db: AsyncSession,
        symbols: List[str]
    ) -> Dict[str, Any]:
        """Check availability of current price data"""
        
        # Get most recent price data for each symbol
        recent_cutoff = utc_now() - timedelta(days=7)  # Look back 1 week max
        
        stmt = select(
            MarketDataCache.symbol,
            func.max(MarketDataCache.date).label('latest_date'),
            func.count(MarketDataCache.close).label('price_count')
        ).where(
            and_(
                MarketDataCache.symbol.in_([s.upper() for s in symbols]),
                MarketDataCache.date >= recent_cutoff.date(),
                MarketDataCache.close.is_not(None)
            )
        ).group_by(MarketDataCache.symbol)
        
        result = await db.execute(stmt)
        records = result.all()
        
        # Build coverage map
        coverage_map = {}
        for record in records:
            coverage_map[record.symbol] = {
                'has_data': True,
                'latest_date': record.latest_date,
                'price_count': record.price_count
            }
        
        # Add missing symbols
        for symbol in symbols:
            if symbol.upper() not in coverage_map:
                coverage_map[symbol.upper()] = {
                    'has_data': False,
                    'latest_date': None,
                    'price_count': 0
                }
        
        # Calculate coverage percentage
        symbols_with_data = sum(1 for info in coverage_map.values() if info['has_data'])
        coverage_percentage = symbols_with_data / len(symbols) if symbols else 0
        
        return {
            'coverage_percentage': coverage_percentage,
            'symbols_with_data': symbols_with_data,
            'total_symbols': len(symbols),
            'symbol_details': coverage_map,
            'missing_symbols': [
                symbol for symbol, info in coverage_map.items() 
                if not info['has_data']
            ]
        }
    
    async def _check_historical_data_coverage(
        self,
        db: AsyncSession,
        symbols: List[str]
    ) -> Dict[str, Any]:
        """Check availability of historical data for factor analysis"""
        
        # Check for minimum historical days (default 30)
        min_date = date.today() - timedelta(days=self.quality_thresholds['minimum_historical_days'])
        
        stmt = select(
            MarketDataCache.symbol,
            func.count(MarketDataCache.date).label('historical_days'),
            func.min(MarketDataCache.date).label('first_date'),
            func.max(MarketDataCache.date).label('last_date')
        ).where(
            and_(
                MarketDataCache.symbol.in_([s.upper() for s in symbols]),
                MarketDataCache.date >= min_date,
                MarketDataCache.close.is_not(None)
            )
        ).group_by(MarketDataCache.symbol)
        
        result = await db.execute(stmt)
        records = result.all()
        
        # Build historical coverage map
        historical_map = {}
        for record in records:
            has_sufficient = record.historical_days >= self.quality_thresholds['minimum_historical_days']
            historical_map[record.symbol] = {
                'has_sufficient_data': has_sufficient,
                'historical_days': record.historical_days,
                'first_date': record.first_date,
                'last_date': record.last_date
            }
        
        # Add missing symbols
        for symbol in symbols:
            if symbol.upper() not in historical_map:
                historical_map[symbol.upper()] = {
                    'has_sufficient_data': False,
                    'historical_days': 0,
                    'first_date': None,
                    'last_date': None
                }
        
        # Calculate coverage
        symbols_with_sufficient = sum(
            1 for info in historical_map.values() 
            if info['has_sufficient_data']
        )
        coverage_percentage = symbols_with_sufficient / len(symbols) if symbols else 0
        
        return {
            'coverage_percentage': coverage_percentage,
            'symbols_with_sufficient_data': symbols_with_sufficient,
            'total_symbols': len(symbols),
            'required_days': self.quality_thresholds['minimum_historical_days'],
            'symbol_details': historical_map,
            'insufficient_symbols': [
                symbol for symbol, info in historical_map.items()
                if not info['has_sufficient_data']
            ]
        }
    
    async def _check_data_freshness(
        self,
        db: AsyncSession,
        symbols: List[str]
    ) -> Dict[str, Any]:
        """Check if data is fresh enough for batch processing"""
        
        freshness_cutoff = utc_now() - timedelta(hours=self.quality_thresholds['data_freshness_hours'])
        
        stmt = select(
            MarketDataCache.symbol,
            func.max(MarketDataCache.date).label('latest_date')
        ).where(
            MarketDataCache.symbol.in_([s.upper() for s in symbols])
        ).group_by(MarketDataCache.symbol)
        
        result = await db.execute(stmt)
        records = result.all()
        
        # Check freshness
        freshness_map = {}
        for record in records:
            if record.latest_date:
                # Convert date to datetime for comparison
                latest_datetime = datetime.combine(record.latest_date, datetime.min.time())
                is_fresh = latest_datetime >= freshness_cutoff
                hours_old = (utc_now() - latest_datetime).total_seconds() / 3600
                
                freshness_map[record.symbol] = {
                    'is_fresh': is_fresh,
                    'latest_date': record.latest_date,
                    'hours_old': hours_old
                }
            else:
                freshness_map[record.symbol] = {
                    'is_fresh': False,
                    'latest_date': None,
                    'hours_old': float('inf')
                }
        
        # Add missing symbols
        for symbol in symbols:
            if symbol.upper() not in freshness_map:
                freshness_map[symbol.upper()] = {
                    'is_fresh': False,
                    'latest_date': None,
                    'hours_old': float('inf')
                }
        
        # Calculate freshness percentage
        fresh_symbols = sum(1 for info in freshness_map.values() if info['is_fresh'])
        freshness_percentage = fresh_symbols / len(symbols) if symbols else 0
        
        return {
            'freshness_percentage': freshness_percentage,
            'fresh_symbols': fresh_symbols,
            'total_symbols': len(symbols),
            'freshness_threshold_hours': self.quality_thresholds['data_freshness_hours'],
            'symbol_details': freshness_map,
            'stale_symbols': [
                symbol for symbol, info in freshness_map.items()
                if not info['is_fresh']
            ]
        }
    
    def _calculate_quality_score(
        self,
        current_coverage: Dict[str, Any],
        historical_coverage: Dict[str, Any],
        freshness_results: Dict[str, Any]
    ) -> float:
        """Calculate overall data quality score"""
        
        # Weighted average of different quality metrics
        weights = {
            'current_coverage': 0.4,
            'historical_coverage': 0.3,
            'freshness': 0.3
        }
        
        quality_score = (
            current_coverage['coverage_percentage'] * weights['current_coverage'] +
            historical_coverage['coverage_percentage'] * weights['historical_coverage'] +
            freshness_results['freshness_percentage'] * weights['freshness']
        )
        
        return quality_score
    
    def _generate_recommendations(
        self,
        current_coverage: Dict[str, Any],
        historical_coverage: Dict[str, Any],
        freshness_results: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on validation results"""
        
        recommendations = []
        
        # Check current price coverage
        if current_coverage['coverage_percentage'] < self.quality_thresholds['minimum_coverage']:
            missing_count = len(current_coverage['missing_symbols'])
            recommendations.append(
                f"Update market data for {missing_count} symbols: "
                f"{', '.join(current_coverage['missing_symbols'][:5])}"
                + ("..." if missing_count > 5 else "")
            )
        
        # Check historical data
        if historical_coverage['coverage_percentage'] < self.quality_thresholds['minimum_coverage']:
            insufficient_count = len(historical_coverage['insufficient_symbols'])
            recommendations.append(
                f"Fetch historical data for {insufficient_count} symbols with <{historical_coverage['required_days']} days of data"
            )
        
        # Check freshness
        if freshness_results['freshness_percentage'] < self.quality_thresholds['minimum_coverage']:
            stale_count = len(freshness_results['stale_symbols'])
            recommendations.append(
                f"Refresh stale data for {stale_count} symbols (>{freshness_results['freshness_threshold_hours']}h old)"
            )
        
        if not recommendations:
            recommendations.append("Data quality is within acceptable thresholds")
        
        return recommendations


# Convenience function for batch orchestrator integration
async def pre_flight_validation(
    db: AsyncSession,
    portfolio_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Perform pre-flight data quality validation before batch processing
    
    Args:
        db: Database session
        portfolio_id: Optional portfolio to validate
        
    Returns:
        Validation results with pass/fail status and recommendations
    """
    validator = DataQualityValidator()
    return await validator.validate_data_coverage(db, portfolio_id)
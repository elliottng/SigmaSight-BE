"""
Comprehensive Stress Testing Framework - Section 1.4.7
Implements advanced stress testing with factor correlation modeling and predefined scenarios
"""
import json
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from uuid import UUID
import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.positions import Position
from app.models.market_data import FactorDefinition, PositionFactorExposure, FactorExposure
from app.models.users import Portfolio
from app.calculations.factors import fetch_factor_returns
from app.constants.factors import FACTOR_ETFS, REGRESSION_WINDOW_DAYS
from app.core.logging import get_logger

logger = get_logger(__name__)

# Stress testing constants
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config" / "stress_scenarios.json"
DEFAULT_LOOKBACK_DAYS = 252
CORRELATION_DECAY_FACTOR = 0.94
STRESS_MAGNITUDE_CAP = 1.0


async def calculate_factor_correlation_matrix(
    db: AsyncSession,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    decay_factor: float = CORRELATION_DECAY_FACTOR
) -> Dict[str, Any]:
    """
    Calculate factor cross-correlation matrix with exponential decay weighting
    
    Args:
        db: Database session
        lookback_days: Historical period for correlation calculation (default: 252 days)
        decay_factor: Exponential decay factor for historical data weighting (default: 0.94)
        
    Returns:
        Dictionary containing correlation matrix and metadata
    """
    logger.info(f"Calculating factor correlation matrix with {lookback_days} days lookback")
    
    try:
        # Define calculation period
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days + 30)  # Buffer for trading days
        
        # Fetch factor returns
        factor_symbols = list(FACTOR_ETFS.values())
        factor_returns = await fetch_factor_returns(
            db=db,
            symbols=factor_symbols,
            start_date=start_date,
            end_date=end_date
        )
        
        if factor_returns.empty:
            raise ValueError("No factor returns data available for correlation calculation")
        
        # Ensure we have sufficient data
        if len(factor_returns) < 60:  # Minimum 60 days for meaningful correlation
            logger.warning(f"Limited data for correlation: {len(factor_returns)} days")
        
        # Calculate exponentially weighted correlation matrix
        correlation_matrix = {}
        factor_names = factor_returns.columns.tolist()
        
        # Apply exponential decay weights (more recent data gets higher weight)
        weights = np.array([decay_factor ** i for i in range(len(factor_returns))])
        weights = weights[::-1]  # Reverse so recent data has higher weight
        weights = weights / weights.sum()  # Normalize weights
        
        # Calculate weighted correlation matrix
        for i, factor1 in enumerate(factor_names):
            correlation_matrix[factor1] = {}
            for j, factor2 in enumerate(factor_names):
                if factor1 == factor2:
                    correlation_matrix[factor1][factor2] = 1.0
                else:
                    # Calculate weighted correlation
                    data1 = factor_returns[factor1].values
                    data2 = factor_returns[factor2].values
                    
                    # Remove any NaN values
                    mask = ~(np.isnan(data1) | np.isnan(data2))
                    data1_clean = data1[mask]
                    data2_clean = data2[mask]
                    weights_clean = weights[mask]
                    
                    if len(data1_clean) < 30:  # Minimum data for correlation
                        correlation_matrix[factor1][factor2] = 0.0
                        continue
                    
                    # Weighted covariance and correlation
                    mean1 = np.average(data1_clean, weights=weights_clean)
                    mean2 = np.average(data2_clean, weights=weights_clean)
                    
                    cov = np.average((data1_clean - mean1) * (data2_clean - mean2), weights=weights_clean)
                    var1 = np.average((data1_clean - mean1) ** 2, weights=weights_clean)
                    var2 = np.average((data2_clean - mean2) ** 2, weights=weights_clean)
                    
                    if var1 > 0 and var2 > 0:
                        correlation = cov / (np.sqrt(var1) * np.sqrt(var2))
                        # Cap correlation between -0.95 and 0.95 to prevent extreme values
                        correlation = max(-0.95, min(0.95, correlation))
                        correlation_matrix[factor1][factor2] = float(correlation)
                    else:
                        correlation_matrix[factor1][factor2] = 0.0
        
        # Calculate matrix statistics
        correlations_flat = []
        for factor1 in factor_names:
            for factor2 in factor_names:
                if factor1 != factor2:
                    correlations_flat.append(correlation_matrix[factor1][factor2])
        
        results = {
            'correlation_matrix': correlation_matrix,
            'factor_names': factor_names,
            'calculation_date': end_date,
            'lookback_days': lookback_days,
            'decay_factor': decay_factor,
            'data_days': len(factor_returns),
            'matrix_stats': {
                'mean_correlation': float(np.mean(correlations_flat)),
                'max_correlation': float(np.max(correlations_flat)),
                'min_correlation': float(np.min(correlations_flat)),
                'std_correlation': float(np.std(correlations_flat))
            }
        }
        
        logger.info(f"Factor correlation matrix calculated: {len(factor_names)} factors, "
                   f"mean correlation: {results['matrix_stats']['mean_correlation']:.3f}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error calculating factor correlation matrix: {str(e)}")
        raise


def load_stress_scenarios(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load stress scenario definitions from JSON configuration file
    
    Args:
        config_path: Path to JSON configuration file (defaults to built-in scenarios)
        
    Returns:
        Dictionary containing parsed stress scenario definitions
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    
    logger.info(f"Loading stress scenarios from {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate configuration structure
        required_keys = ['stress_scenarios', 'configuration', 'factor_mappings']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        # Count active scenarios
        total_scenarios = 0
        active_scenarios = 0
        
        for category, scenarios in config['stress_scenarios'].items():
            for scenario_id, scenario in scenarios.items():
                total_scenarios += 1
                if scenario.get('active', True):
                    active_scenarios += 1
        
        logger.info(f"Loaded {active_scenarios}/{total_scenarios} active stress scenarios")
        
        return config
        
    except FileNotFoundError:
        logger.error(f"Stress scenarios configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in stress scenarios configuration: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error loading stress scenarios: {str(e)}")
        raise


async def calculate_direct_stress_impact(
    db: AsyncSession,
    portfolio_id: UUID,
    scenario_config: Dict[str, Any],
    calculation_date: date
) -> Dict[str, Any]:
    """
    Calculate direct impact of stress scenario without factor correlations
    
    Args:
        db: Database session
        portfolio_id: Portfolio ID to analyze
        scenario_config: Single scenario configuration from JSON
        calculation_date: Date for calculation
        
    Returns:
        Dictionary containing direct stress impact results
    """
    logger.info(f"Calculating direct stress impact for scenario: {scenario_config.get('name')}")
    
    try:
        # Get portfolio factor exposures
        stmt = select(FactorExposure).where(
            and_(
                FactorExposure.portfolio_id == portfolio_id,
                FactorExposure.calculation_date <= calculation_date
            )
        ).order_by(FactorExposure.calculation_date.desc()).limit(50)  # Get recent exposures
        
        result = await db.execute(stmt)
        factor_exposures = result.scalars().all()
        
        if not factor_exposures:
            raise ValueError(f"No factor exposures found for portfolio {portfolio_id}")
        
        # Get the most recent factor exposures
        latest_exposures = {}
        for exposure in factor_exposures:
            # Get factor definition to map to factor name
            stmt = select(FactorDefinition).where(FactorDefinition.id == exposure.factor_id)
            result = await db.execute(stmt)
            factor_def = result.scalar_one_or_none()
            
            if factor_def and factor_def.name not in latest_exposures:
                latest_exposures[factor_def.name] = {
                    'exposure_value': float(exposure.exposure_value),
                    'exposure_dollar': float(exposure.exposure_dollar) if exposure.exposure_dollar else 0.0,
                    'calculation_date': exposure.calculation_date
                }
        
        # Calculate direct impact for each shocked factor
        shocked_factors = scenario_config.get('shocked_factors', {})
        direct_impacts = {}
        total_direct_pnl = 0.0
        
        for factor_name, shock_amount in shocked_factors.items():
            if factor_name in latest_exposures:
                exposure_dollar = latest_exposures[factor_name]['exposure_dollar']
                # Direct P&L = Factor Exposure × Shock Amount
                factor_pnl = exposure_dollar * shock_amount
                direct_impacts[factor_name] = {
                    'exposure_dollar': exposure_dollar,
                    'shock_amount': shock_amount,
                    'factor_pnl': factor_pnl
                }
                total_direct_pnl += factor_pnl
                
                logger.debug(f"Factor {factor_name}: ${exposure_dollar:,.0f} exposure × "
                           f"{shock_amount:+.1%} shock = ${factor_pnl:,.0f} P&L")
            else:
                logger.warning(f"No exposure found for shocked factor: {factor_name}")
                direct_impacts[factor_name] = {
                    'exposure_dollar': 0.0,
                    'shock_amount': shock_amount,
                    'factor_pnl': 0.0
                }
        
        results = {
            'scenario_name': scenario_config.get('name'),
            'scenario_id': scenario_config.get('id'),
            'portfolio_id': str(portfolio_id),
            'calculation_date': calculation_date,
            'shocked_factors': shocked_factors,
            'factor_impacts': direct_impacts,
            'total_direct_pnl': total_direct_pnl,
            'calculation_method': 'direct',
            'factor_exposures_date': max([exp['calculation_date'] for exp in latest_exposures.values()]) if latest_exposures else calculation_date
        }
        
        logger.info(f"Direct stress impact calculated: ${total_direct_pnl:,.0f} total P&L")
        return results
        
    except Exception as e:
        logger.error(f"Error calculating direct stress impact: {str(e)}")
        raise


async def calculate_correlated_stress_impact(
    db: AsyncSession,
    portfolio_id: UUID,
    scenario_config: Dict[str, Any],
    correlation_matrix: Dict[str, Dict[str, float]],
    calculation_date: date
) -> Dict[str, Any]:
    """
    Calculate total stress impact including cross-factor correlations
    
    Args:
        db: Database session
        portfolio_id: Portfolio ID to analyze
        scenario_config: Single scenario configuration from JSON
        correlation_matrix: Factor correlation matrix from calculate_factor_correlation_matrix()
        calculation_date: Date for calculation
        
    Returns:
        Dictionary containing correlated stress impact results
    """
    logger.info(f"Calculating correlated stress impact for scenario: {scenario_config.get('name')}")
    
    try:
        # First get direct impact
        direct_results = await calculate_direct_stress_impact(
            db=db,
            portfolio_id=portfolio_id,
            scenario_config=scenario_config,
            calculation_date=calculation_date
        )
        
        # Get portfolio factor exposures (reuse from direct calculation)
        stmt = select(FactorExposure).where(
            and_(
                FactorExposure.portfolio_id == portfolio_id,
                FactorExposure.calculation_date <= calculation_date
            )
        ).order_by(FactorExposure.calculation_date.desc()).limit(50)
        
        result = await db.execute(stmt)
        factor_exposures = result.scalars().all()
        
        # Map factor exposures by name
        latest_exposures = {}
        for exposure in factor_exposures:
            stmt = select(FactorDefinition).where(FactorDefinition.id == exposure.factor_id)
            result = await db.execute(stmt)
            factor_def = result.scalar_one_or_none()
            
            if factor_def and factor_def.name not in latest_exposures:
                latest_exposures[factor_def.name] = {
                    'exposure_value': float(exposure.exposure_value),
                    'exposure_dollar': float(exposure.exposure_dollar) if exposure.exposure_dollar else 0.0
                }
        
        # Calculate correlated impacts
        shocked_factors = scenario_config.get('shocked_factors', {})
        correlated_impacts = {}
        total_correlated_pnl = 0.0
        
        # For each factor in the portfolio, calculate its correlated response
        for factor_name, exposure_data in latest_exposures.items():
            factor_impact = 0.0
            impact_breakdown = {}
            
            # Calculate impact from each shocked factor via correlation
            for shocked_factor, shock_amount in shocked_factors.items():
                if shocked_factor in correlation_matrix and factor_name in correlation_matrix[shocked_factor]:
                    correlation = correlation_matrix[shocked_factor][factor_name]
                    # Correlated shock = Original shock × Correlation × Factor exposure
                    correlated_shock = shock_amount * correlation
                    correlated_pnl = exposure_data['exposure_dollar'] * correlated_shock
                    
                    factor_impact += correlated_pnl
                    impact_breakdown[shocked_factor] = {
                        'original_shock': shock_amount,
                        'correlation': correlation,
                        'correlated_shock': correlated_shock,
                        'correlated_pnl': correlated_pnl
                    }
                elif shocked_factor == factor_name:
                    # Direct impact (correlation = 1.0)
                    direct_pnl = exposure_data['exposure_dollar'] * shock_amount
                    factor_impact += direct_pnl
                    impact_breakdown[shocked_factor] = {
                        'original_shock': shock_amount,
                        'correlation': 1.0,
                        'correlated_shock': shock_amount,
                        'correlated_pnl': direct_pnl
                    }
            
            correlated_impacts[factor_name] = {
                'exposure_dollar': exposure_data['exposure_dollar'],
                'total_factor_impact': factor_impact,
                'impact_breakdown': impact_breakdown
            }
            
            total_correlated_pnl += factor_impact
        
        results = {
            'scenario_name': scenario_config.get('name'),
            'scenario_id': scenario_config.get('id'),
            'portfolio_id': str(portfolio_id),
            'calculation_date': calculation_date,
            'shocked_factors': shocked_factors,
            'direct_pnl': direct_results['total_direct_pnl'],
            'correlated_pnl': total_correlated_pnl,
            'correlation_effect': total_correlated_pnl - direct_results['total_direct_pnl'],
            'factor_impacts': correlated_impacts,
            'calculation_method': 'correlated',
            'correlation_matrix_stats': {
                'factors_used': len(correlation_matrix),
                'shocked_factors': list(shocked_factors.keys())
            }
        }
        
        logger.info(f"Correlated stress impact calculated: ${total_correlated_pnl:,.0f} total P&L "
                   f"(correlation effect: ${results['correlation_effect']:,.0f})")
        
        return results
        
    except Exception as e:
        logger.error(f"Error calculating correlated stress impact: {str(e)}")
        raise


async def run_comprehensive_stress_test(
    db: AsyncSession,
    portfolio_id: UUID,
    calculation_date: date,
    scenario_filter: Optional[List[str]] = None,
    config_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Run comprehensive stress test for all scenarios
    
    Args:
        db: Database session
        portfolio_id: Portfolio ID to analyze
        calculation_date: Date for calculation
        scenario_filter: Optional list of scenario categories to include
        config_path: Optional path to custom scenario configuration
        
    Returns:
        Dictionary containing complete stress test results
    """
    logger.info(f"Running comprehensive stress test for portfolio {portfolio_id}")
    
    try:
        # Load stress scenarios
        config = load_stress_scenarios(config_path)
        
        # Calculate factor correlation matrix
        correlation_data = await calculate_factor_correlation_matrix(db)
        correlation_matrix = correlation_data['correlation_matrix']
        
        # Get portfolio information
        stmt = select(Portfolio).where(Portfolio.id == portfolio_id)
        result = await db.execute(stmt)
        portfolio = result.scalar_one_or_none()
        
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        # Run stress tests for all active scenarios
        stress_results = {
            'direct_impacts': {},
            'correlated_impacts': {},
            'summary_stats': {},
            'scenarios_tested': 0,
            'scenarios_skipped': 0
        }
        
        total_scenarios = 0
        processed_scenarios = 0
        
        for category, scenarios in config['stress_scenarios'].items():
            # Apply scenario filter if provided
            if scenario_filter and category not in scenario_filter:
                continue
                
            stress_results['direct_impacts'][category] = {}
            stress_results['correlated_impacts'][category] = {}
            
            for scenario_id, scenario_config in scenarios.items():
                total_scenarios += 1
                
                # Skip inactive scenarios
                if not scenario_config.get('active', True):
                    stress_results['scenarios_skipped'] += 1
                    continue
                
                try:
                    # Add scenario ID to config for tracking
                    scenario_config['id'] = scenario_id
                    
                    # Calculate direct impact
                    direct_result = await calculate_direct_stress_impact(
                        db=db,
                        portfolio_id=portfolio_id,
                        scenario_config=scenario_config,
                        calculation_date=calculation_date
                    )
                    stress_results['direct_impacts'][category][scenario_id] = direct_result
                    
                    # Calculate correlated impact
                    correlated_result = await calculate_correlated_stress_impact(
                        db=db,
                        portfolio_id=portfolio_id,
                        scenario_config=scenario_config,
                        correlation_matrix=correlation_matrix,
                        calculation_date=calculation_date
                    )
                    stress_results['correlated_impacts'][category][scenario_id] = correlated_result
                    
                    processed_scenarios += 1
                    
                except Exception as e:
                    logger.error(f"Error processing scenario {scenario_id}: {str(e)}")
                    stress_results['scenarios_skipped'] += 1
        
        stress_results['scenarios_tested'] = processed_scenarios
        
        # Calculate summary statistics
        all_direct_pnls = []
        all_correlated_pnls = []
        
        for category in stress_results['direct_impacts']:
            for scenario_id in stress_results['direct_impacts'][category]:
                direct_pnl = stress_results['direct_impacts'][category][scenario_id]['total_direct_pnl']
                correlated_pnl = stress_results['correlated_impacts'][category][scenario_id]['correlated_pnl']
                
                all_direct_pnls.append(direct_pnl)
                all_correlated_pnls.append(correlated_pnl)
        
        if all_correlated_pnls:
            stress_results['summary_stats'] = {
                'worst_case_pnl': float(min(all_correlated_pnls)),
                'best_case_pnl': float(max(all_correlated_pnls)),
                'mean_pnl': float(np.mean(all_correlated_pnls)),
                'median_pnl': float(np.median(all_correlated_pnls)),
                'pnl_std': float(np.std(all_correlated_pnls)),
                'mean_correlation_effect': float(np.mean([c - d for c, d in zip(all_correlated_pnls, all_direct_pnls)])),
                'scenarios_negative': len([pnl for pnl in all_correlated_pnls if pnl < 0]),
                'scenarios_positive': len([pnl for pnl in all_correlated_pnls if pnl > 0])
            }
        
        # Compile final results
        final_results = {
            'portfolio_id': str(portfolio_id),
            'portfolio_name': portfolio.name,
            'calculation_date': calculation_date,
            'correlation_matrix_info': {
                'calculation_date': correlation_data['calculation_date'],
                'data_days': correlation_data['data_days'],
                'mean_correlation': correlation_data['matrix_stats']['mean_correlation']
            },
            'stress_test_results': stress_results,
            'config_metadata': {
                'scenarios_available': total_scenarios,
                'scenarios_tested': processed_scenarios,
                'scenarios_skipped': stress_results['scenarios_skipped'],
                'categories_tested': len([cat for cat in stress_results['direct_impacts'] if stress_results['direct_impacts'][cat]])
            }
        }
        
        logger.info(f"Comprehensive stress test completed: {processed_scenarios}/{total_scenarios} scenarios, "
                   f"worst case: ${stress_results['summary_stats'].get('worst_case_pnl', 0):,.0f}")
        
        return final_results
        
    except Exception as e:
        logger.error(f"Error running comprehensive stress test: {str(e)}")
        raise
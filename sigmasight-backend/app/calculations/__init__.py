"""
Calculation modules for SigmaSight Backend
Contains quantitative calculations for portfolio analytics
"""

from .market_data import (
    calculate_position_market_value,
    calculate_daily_pnl,
    fetch_and_cache_prices
)

from .greeks import (
    calculate_real_greeks,
    get_mock_greeks
)

from .portfolio import (
    calculate_portfolio_exposures,
    aggregate_portfolio_greeks,
    calculate_delta_adjusted_exposure,
    aggregate_by_tags,
    aggregate_by_underlying,
    clear_portfolio_cache
)

from .snapshots import (
    create_portfolio_snapshot
)

__all__ = [
    # Market data calculations
    "calculate_position_market_value",
    "calculate_daily_pnl",
    "fetch_and_cache_prices",
    
    # Greeks calculations
    "calculate_real_greeks",
    "get_mock_greeks",
    
    # Portfolio aggregations
    "calculate_portfolio_exposures",
    "aggregate_portfolio_greeks",
    "calculate_delta_adjusted_exposure",
    "aggregate_by_tags",
    "aggregate_by_underlying",
    "clear_portfolio_cache",
    
    # Snapshot generation
    "create_portfolio_snapshot"
]
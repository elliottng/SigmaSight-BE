"""
Unit tests for portfolio aggregation functions.

Tests all functions in app/calculations/portfolio.py with various scenarios
including edge cases, large portfolios, and missing data.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
import time
from typing import List, Dict

from app.calculations.portfolio import (
    calculate_portfolio_exposures,
    aggregate_portfolio_greeks,
    calculate_delta_adjusted_exposure,
    aggregate_by_tags,
    aggregate_by_underlying,
    clear_portfolio_cache,
    timed_lru_cache
)


class TestPortfolioExposures:
    """Tests for calculate_portfolio_exposures function."""
    
    def test_empty_portfolio(self):
        """Test empty portfolio returns zeros with metadata."""
        result = calculate_portfolio_exposures([])
        
        assert result["gross_exposure"] == Decimal("0.00")
        assert result["net_exposure"] == Decimal("0.00")
        assert result["long_exposure"] == Decimal("0.00")
        assert result["short_exposure"] == Decimal("0.00")
        assert result["long_count"] == 0
        assert result["short_count"] == 0
        assert result["options_exposure"] == Decimal("0.00")
        assert result["stock_exposure"] == Decimal("0.00")
        assert result["notional"] == Decimal("0.00")
        assert "Empty portfolio" in result["metadata"]["warnings"][0]
    
    def test_single_long_stock(self):
        """Test single long stock position."""
        positions = [{
            "exposure": Decimal("10000"),
            "market_value": Decimal("10000"),
            "position_type": "LONG",
            "quantity": Decimal("100")
        }]
        
        result = calculate_portfolio_exposures(positions)
        
        assert result["gross_exposure"] == Decimal("10000.00")
        assert result["net_exposure"] == Decimal("10000.00")
        assert result["long_exposure"] == Decimal("10000.00")
        assert result["short_exposure"] == Decimal("0.00")
        assert result["long_count"] == 1
        assert result["short_count"] == 0
        assert result["stock_exposure"] == Decimal("10000.00")
        assert result["notional"] == Decimal("10000.00")
    
    def test_mixed_portfolio(self):
        """Test portfolio with mixed long/short stocks and options."""
        positions = [
            # Long stock
            {
                "exposure": Decimal("10000"),
                "market_value": Decimal("10000"),
                "position_type": "LONG",
                "quantity": Decimal("100")
            },
            # Short stock
            {
                "exposure": Decimal("-5000"),
                "market_value": Decimal("-5000"),
                "position_type": "SHORT",
                "quantity": Decimal("-50")
            },
            # Long call option
            {
                "exposure": Decimal("3000"),
                "market_value": Decimal("3000"),
                "position_type": "LC",
                "quantity": Decimal("10")
            },
            # Short put option
            {
                "exposure": Decimal("-2000"),
                "market_value": Decimal("-2000"),
                "position_type": "SP",
                "quantity": Decimal("-5")
            }
        ]
        
        result = calculate_portfolio_exposures(positions)
        
        assert result["gross_exposure"] == Decimal("20000.00")  # 10k + 5k + 3k + 2k
        assert result["net_exposure"] == Decimal("6000.00")     # 10k - 5k + 3k - 2k
        assert result["long_exposure"] == Decimal("13000.00")   # 10k + 3k
        assert result["short_exposure"] == Decimal("-7000.00")  # -5k - 2k
        assert result["long_count"] == 2
        assert result["short_count"] == 2
        assert result["options_exposure"] == Decimal("5000.00") # 3k + 2k
        assert result["stock_exposure"] == Decimal("15000.00")  # 10k + 5k
        assert result["notional"] == Decimal("20000.00")
    
    def test_precision_handling(self):
        """Test that decimal precision is maintained correctly."""
        positions = [{
            "exposure": Decimal("12345.6789"),
            "market_value": Decimal("12345.6789"),
            "position_type": "LONG",
            "quantity": Decimal("123.456")
        }]
        
        result = calculate_portfolio_exposures(positions)
        
        # Should be rounded to 2 decimal places
        assert result["gross_exposure"] == Decimal("12345.68")
        assert result["net_exposure"] == Decimal("12345.68")
        assert str(result["gross_exposure"]) == "12345.68"


class TestPortfolioGreeks:
    """Tests for aggregate_portfolio_greeks function."""
    
    def test_empty_portfolio(self):
        """Test empty portfolio returns zero Greeks."""
        result = aggregate_portfolio_greeks([])
        
        assert result["delta"] == Decimal("0.0000")
        assert result["gamma"] == Decimal("0.0000")
        assert result["theta"] == Decimal("0.0000")
        assert result["vega"] == Decimal("0.0000")
        assert result["rho"] == Decimal("0.0000")
        assert result["metadata"]["positions_with_greeks"] == 0
    
    def test_positions_without_greeks(self):
        """Test that positions without Greeks are skipped."""
        positions = [
            {"greeks": None},  # Stock position
            {"greeks": None},  # Another stock
            {}  # Missing greeks field entirely
        ]
        
        result = aggregate_portfolio_greeks(positions)
        
        assert result["delta"] == Decimal("0.0000")
        assert result["metadata"]["positions_without_greeks"] == 3
        assert "3 positions excluded" in result["metadata"]["warnings"][0]
    
    def test_mixed_greeks_aggregation(self):
        """Test aggregation of multiple positions with Greeks."""
        positions = [
            {
                "greeks": {
                    "delta": Decimal("0.5"),
                    "gamma": Decimal("0.02"),
                    "theta": Decimal("-10"),
                    "vega": Decimal("5"),
                    "rho": Decimal("2")
                }
            },
            {
                "greeks": {
                    "delta": Decimal("-0.3"),
                    "gamma": Decimal("0.01"),
                    "theta": Decimal("-5"),
                    "vega": Decimal("3"),
                    "rho": Decimal("-1")
                }
            },
            {"greeks": None}  # Stock - should be skipped
        ]
        
        result = aggregate_portfolio_greeks(positions)
        
        assert result["delta"] == Decimal("0.2000")  # 0.5 - 0.3
        assert result["gamma"] == Decimal("0.0300")  # 0.02 + 0.01
        assert result["theta"] == Decimal("-15.0000")  # -10 - 5
        assert result["vega"] == Decimal("8.0000")  # 5 + 3
        assert result["rho"] == Decimal("1.0000")  # 2 - 1
        assert result["metadata"]["positions_with_greeks"] == 2
        assert result["metadata"]["positions_without_greeks"] == 1
    
    def test_greeks_precision(self):
        """Test that Greeks maintain 4 decimal places."""
        positions = [{
            "greeks": {
                "delta": Decimal("0.123456789"),
                "gamma": Decimal("0.000123456"),
                "theta": Decimal("-123.456789"),
                "vega": Decimal("12.3456789"),
                "rho": Decimal("1.23456789")
            }
        }]
        
        result = aggregate_portfolio_greeks(positions)
        
        assert result["delta"] == Decimal("0.1235")
        assert result["gamma"] == Decimal("0.0001")
        assert result["theta"] == Decimal("-123.4568")
        assert result["vega"] == Decimal("12.3457")
        assert result["rho"] == Decimal("1.2346")


class TestDeltaAdjustedExposure:
    """Tests for calculate_delta_adjusted_exposure function."""
    
    def test_empty_portfolio(self):
        """Test empty portfolio returns zeros."""
        result = calculate_delta_adjusted_exposure([])
        
        assert result["raw_exposure"] == Decimal("0.00")
        assert result["delta_adjusted_exposure"] == Decimal("0.00")
        assert "Empty portfolio" in result["metadata"]["warnings"][0]
    
    def test_stock_positions(self):
        """Test stocks use implicit delta of 1.0 or -1.0."""
        positions = [
            {
                "exposure": Decimal("10000"),
                "position_type": "LONG",
                "greeks": None
            },
            {
                "exposure": Decimal("-5000"),
                "position_type": "SHORT",
                "greeks": None
            }
        ]
        
        result = calculate_delta_adjusted_exposure(positions)
        
        assert result["raw_exposure"] == Decimal("15000.00")  # abs(10k) + abs(-5k)
        assert result["delta_adjusted_exposure"] == Decimal("5000.00")  # 10k + (-5k)
        assert result["metadata"]["positions_included"] == 2
        assert result["metadata"]["positions_excluded"] == 0
    
    def test_options_with_deltas(self):
        """Test options use their actual delta values."""
        positions = [
            {
                "exposure": Decimal("10000"),
                "position_type": "LC",
                "greeks": {"delta": Decimal("0.6")}
            },
            {
                "exposure": Decimal("-8000"),
                "position_type": "SC",
                "greeks": {"delta": Decimal("-0.4")}
            }
        ]
        
        result = calculate_delta_adjusted_exposure(positions)
        
        assert result["raw_exposure"] == Decimal("18000.00")  # 10k + 8k
        # Delta adjusted: (10k * 0.6) + (-8k * -0.4) = 6k + 3.2k = 9.2k
        assert result["delta_adjusted_exposure"] == Decimal("9200.00")
    
    def test_mixed_with_missing_greeks(self):
        """Test positions without Greeks are excluded."""
        positions = [
            {
                "exposure": Decimal("10000"),
                "position_type": "LC",
                "greeks": {"delta": Decimal("0.5")}
            },
            {
                "exposure": Decimal("5000"),
                "position_type": "LP",
                "greeks": None  # Missing Greeks for option
            },
            {
                "exposure": Decimal("3000"),
                "position_type": "LONG",
                "greeks": None  # Stock - should be included
            }
        ]
        
        result = calculate_delta_adjusted_exposure(positions)
        
        assert result["raw_exposure"] == Decimal("18000.00")
        # Delta adjusted: (10k * 0.5) + (3k * 1.0) = 5k + 3k = 8k
        assert result["delta_adjusted_exposure"] == Decimal("8000.00")
        assert result["metadata"]["positions_included"] == 2
        assert result["metadata"]["positions_excluded"] == 1
        assert "1 positions excluded" in result["metadata"]["warnings"][0]


class TestAggregateByTags:
    """Tests for aggregate_by_tags function."""
    
    def test_no_tags(self):
        """Test positions without tags are skipped."""
        positions = [
            {"exposure": Decimal("10000"), "tags": []},
            {"exposure": Decimal("5000")}  # No tags field
        ]
        
        result = aggregate_by_tags(positions)
        
        assert len(result) == 1  # Only metadata
        assert result["metadata"]["tags_found"] == 0
        assert "No positions matched" in result["metadata"]["warnings"][0]
    
    def test_single_tag_aggregation(self):
        """Test aggregation by single tag."""
        positions = [
            {"exposure": Decimal("10000"), "tags": ["tech"]},
            {"exposure": Decimal("5000"), "tags": ["tech"]},
            {"exposure": Decimal("-3000"), "tags": ["finance"]}
        ]
        
        result = aggregate_by_tags(positions)
        
        assert "tech" in result
        assert result["tech"]["gross_exposure"] == Decimal("15000.00")
        assert result["tech"]["net_exposure"] == Decimal("15000.00")
        assert result["tech"]["position_count"] == 2
        
        assert "finance" in result
        assert result["finance"]["gross_exposure"] == Decimal("3000.00")
        assert result["finance"]["net_exposure"] == Decimal("-3000.00")
        assert result["finance"]["position_count"] == 1
    
    def test_multiple_tags_per_position(self):
        """Test positions with multiple tags count in each tag."""
        positions = [
            {"exposure": Decimal("10000"), "tags": ["tech", "momentum", "large-cap"]},
            {"exposure": Decimal("5000"), "tags": ["tech", "value"]}
        ]
        
        result = aggregate_by_tags(positions)
        
        # Tech should have both positions
        assert result["tech"]["gross_exposure"] == Decimal("15000.00")
        assert result["tech"]["position_count"] == 2
        
        # Momentum should have only first position
        assert result["momentum"]["gross_exposure"] == Decimal("10000.00")
        assert result["momentum"]["position_count"] == 1
        
        # Value should have only second position
        assert result["value"]["gross_exposure"] == Decimal("5000.00")
        assert result["value"]["position_count"] == 1
    
    def test_tag_filter_any_mode(self):
        """Test tag filtering with 'any' mode (OR logic)."""
        positions = [
            {"exposure": Decimal("10000"), "tags": ["tech", "momentum"]},
            {"exposure": Decimal("5000"), "tags": ["tech", "value"]},
            {"exposure": Decimal("3000"), "tags": ["finance", "value"]},
            {"exposure": Decimal("2000"), "tags": ["energy"]}
        ]
        
        # Filter for tech OR value
        result = aggregate_by_tags(positions, tag_filter=["tech", "value"], tag_mode="any")
        
        # Should include first 3 positions
        assert "tech" in result
        assert result["tech"]["position_count"] == 2
        assert result["tech"]["gross_exposure"] == Decimal("15000.00")
        
        assert "value" in result
        assert result["value"]["position_count"] == 2
        assert result["value"]["gross_exposure"] == Decimal("8000.00")
        
        # Should NOT include other tags
        assert "finance" not in result
        assert "energy" not in result
        assert "momentum" not in result
    
    def test_tag_filter_all_mode(self):
        """Test tag filtering with 'all' mode (AND logic)."""
        positions = [
            {"exposure": Decimal("10000"), "tags": ["tech", "momentum", "growth"]},
            {"exposure": Decimal("5000"), "tags": ["tech", "momentum"]},
            {"exposure": Decimal("3000"), "tags": ["tech", "value"]}
        ]
        
        # Filter for positions with BOTH tech AND momentum
        result = aggregate_by_tags(positions, tag_filter=["tech", "momentum"], tag_mode="all")
        
        # Should only include first two positions
        assert "tech" in result
        assert result["tech"]["position_count"] == 2
        assert result["tech"]["gross_exposure"] == Decimal("15000.00")
        
        assert "momentum" in result
        assert result["momentum"]["position_count"] == 2
        
        # Growth tag should also be included for first position
        assert "growth" not in result  # Not in filter list
    
    def test_single_tag_filter_string(self):
        """Test that single tag filter as string works."""
        positions = [
            {"exposure": Decimal("10000"), "tags": ["tech"]},
            {"exposure": Decimal("5000"), "tags": ["finance"]}
        ]
        
        # Pass tag_filter as string instead of list
        result = aggregate_by_tags(positions, tag_filter="tech")
        
        assert "tech" in result
        assert result["tech"]["position_count"] == 1
        assert "finance" not in result


class TestAggregateByUnderlying:
    """Tests for aggregate_by_underlying function."""
    
    def test_stocks_only(self):
        """Test aggregation of stocks by symbol."""
        positions = [
            {
                "symbol": "AAPL",
                "exposure": Decimal("10000"),
                "position_type": "LONG",
                "greeks": None
            },
            {
                "symbol": "AAPL", 
                "exposure": Decimal("-5000"),
                "position_type": "SHORT",
                "greeks": None
            },
            {
                "symbol": "MSFT",
                "exposure": Decimal("8000"),
                "position_type": "LONG",
                "greeks": None
            }
        ]
        
        result = aggregate_by_underlying(positions)
        
        assert "AAPL" in result
        assert result["AAPL"]["gross_exposure"] == Decimal("15000.00")
        assert result["AAPL"]["net_exposure"] == Decimal("5000.00")
        assert result["AAPL"]["stock_count"] == 2
        assert result["AAPL"]["option_count"] == 0
        
        assert "MSFT" in result
        assert result["MSFT"]["gross_exposure"] == Decimal("8000.00")
        assert result["MSFT"]["stock_count"] == 1
    
    def test_options_aggregation(self):
        """Test options aggregate by underlying_symbol."""
        positions = [
            {
                "symbol": "AAPL_240119C150",
                "underlying_symbol": "AAPL",
                "exposure": Decimal("5000"),
                "position_type": "LC",
                "greeks": {"delta": Decimal("0.6")}
            },
            {
                "symbol": "AAPL_240119P145", 
                "underlying_symbol": "AAPL",
                "exposure": Decimal("-3000"),
                "position_type": "SP",
                "greeks": {"delta": Decimal("0.4")}
            }
        ]
        
        result = aggregate_by_underlying(positions)
        
        assert "AAPL" in result
        assert result["AAPL"]["gross_exposure"] == Decimal("8000.00")
        assert result["AAPL"]["net_exposure"] == Decimal("2000.00")
        assert result["AAPL"]["option_count"] == 2
        assert result["AAPL"]["call_count"] == 1
        assert result["AAPL"]["put_count"] == 1
        assert result["AAPL"]["greeks"]["delta"] == Decimal("1.0000")  # 0.6 + 0.4
    
    def test_mixed_stocks_and_options(self):
        """Test aggregation of both stocks and options for same underlying."""
        positions = [
            # AAPL stock
            {
                "symbol": "AAPL",
                "exposure": Decimal("10000"),
                "position_type": "LONG",
                "greeks": None
            },
            # AAPL call option
            {
                "symbol": "AAPL_240119C150",
                "underlying_symbol": "AAPL",
                "exposure": Decimal("3000"),
                "position_type": "LC",
                "greeks": {"delta": Decimal("0.5"), "gamma": Decimal("0.02")}
            },
            # SPY put option
            {
                "symbol": "SPY_240119P420",
                "underlying_symbol": "SPY",
                "exposure": Decimal("-2000"),
                "position_type": "SP",
                "greeks": {"delta": Decimal("0.3"), "gamma": Decimal("0.01")}
            }
        ]
        
        result = aggregate_by_underlying(positions)
        
        # AAPL should have both stock and option
        assert result["AAPL"]["gross_exposure"] == Decimal("13000.00")
        assert result["AAPL"]["net_exposure"] == Decimal("13000.00")
        assert result["AAPL"]["stock_count"] == 1
        assert result["AAPL"]["option_count"] == 1
        assert result["AAPL"]["greeks"]["delta"] == Decimal("0.5000")
        assert result["AAPL"]["greeks"]["gamma"] == Decimal("0.0200")
        
        # SPY should have only option
        assert result["SPY"]["gross_exposure"] == Decimal("2000.00")
        assert result["SPY"]["option_count"] == 1
        assert result["SPY"]["put_count"] == 1
    
    def test_missing_underlying_symbol(self):
        """Test positions with missing underlying are skipped."""
        positions = [
            {"symbol": "AAPL", "exposure": Decimal("10000"), "position_type": "LONG"},
            {"exposure": Decimal("5000"), "position_type": "LC"},  # Missing both symbol fields
            {
                "symbol": "MSFT_240119C300",
                "exposure": Decimal("3000"), 
                "position_type": "LC"
                # Missing underlying_symbol for option
            }
        ]
        
        result = aggregate_by_underlying(positions)
        
        # Only AAPL should be included
        assert "AAPL" in result
        assert len(result) == 2  # AAPL + metadata
        assert result["metadata"]["underlyings_found"] == 1
        
        # Check that AAPL has the right values
        assert result["AAPL"]["gross_exposure"] == Decimal("10000.00")
        assert result["AAPL"]["stock_count"] == 1
        assert result["AAPL"]["option_count"] == 0


class TestCaching:
    """Tests for caching functionality."""
    
    def test_timed_lru_cache_basic(self):
        """Test basic caching functionality."""
        call_count = 0
        
        @timed_lru_cache(seconds=1)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        assert expensive_function(5) == 10
        assert call_count == 1
        
        # Second call should use cache
        assert expensive_function(5) == 10
        assert call_count == 1
        
        # Different argument should trigger new call
        assert expensive_function(10) == 20
        assert call_count == 2
    
    def test_timed_lru_cache_expiration(self):
        """Test cache expiration after TTL."""
        call_count = 0
        
        @timed_lru_cache(seconds=0.1)  # 100ms TTL
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        assert expensive_function(5) == 10
        assert call_count == 1
        
        # Second call within TTL
        assert expensive_function(5) == 10
        assert call_count == 1
        
        # Wait for cache to expire
        time.sleep(0.15)
        
        # Third call after expiration
        assert expensive_function(5) == 10
        assert call_count == 2
    
    def test_cache_clear_utility(self):
        """Test clear_portfolio_cache utility function."""
        # This mainly tests that the function runs without error
        # Actual cache clearing is tested indirectly through other tests
        clear_portfolio_cache()  # Should not raise any exceptions


class TestLargePortfolio:
    """Performance tests with large portfolios."""
    
    def test_performance_10k_positions(self):
        """Test aggregation performance with 10,000 positions."""
        # Generate 10,000 positions
        positions = []
        for i in range(10000):
            position_type = "LONG" if i % 2 == 0 else "LC"
            is_option = position_type in ["LC", "LP", "SC", "SP"]
            
            position = {
                "exposure": Decimal(str(1000 + i)),
                "market_value": Decimal(str(1000 + i)),
                "position_type": position_type,
                "quantity": Decimal(str(10 + i % 100)),
                "symbol": f"SYM{i % 100}" if not is_option else f"SYM{i % 100}_240119C{100 + i % 50}",
                "tags": [f"tag{i % 10}", f"strategy{i % 5}"]
            }
            
            if is_option:
                position["underlying_symbol"] = f"SYM{i % 100}"
                position["greeks"] = {
                    "delta": Decimal(str(0.5 + (i % 10) / 20)),
                    "gamma": Decimal(str(0.01 + (i % 5) / 100)),
                    "theta": Decimal(str(-10 - i % 20)),
                    "vega": Decimal(str(5 + i % 10)),
                    "rho": Decimal(str(1 + i % 5))
                }
            else:
                position["greeks"] = None
            
            positions.append(position)
        
        # Test exposure calculation performance
        start = time.time()
        result = calculate_portfolio_exposures(positions)
        elapsed = time.time() - start
        
        assert elapsed < 1.0  # Should complete in under 1 second
        assert result["metadata"]["position_count"] == 10000
        
        # Test Greeks aggregation performance
        start = time.time()
        greeks_result = aggregate_portfolio_greeks(positions)
        elapsed = time.time() - start
        
        assert elapsed < 1.0
        assert greeks_result["metadata"]["positions_with_greeks"] == 5000  # Half are options
        
        # Test tag aggregation performance
        start = time.time()
        tags_result = aggregate_by_tags(positions)
        elapsed = time.time() - start
        
        assert elapsed < 1.0
        assert len(tags_result) >= 10  # At least 10 unique tags + metadata
        
        # Test underlying aggregation performance
        start = time.time()
        underlying_result = aggregate_by_underlying(positions)
        elapsed = time.time() - start
        
        assert elapsed < 1.0
        assert len(underlying_result) >= 100  # 100 unique symbols + metadata


class TestEdgeCases:
    """Tests for edge cases and error conditions."""
    
    def test_none_values_handling(self):
        """Test handling of None values in position data."""
        positions = [
            {
                "exposure": None,  # Will be converted to 0
                "market_value": None,
                "position_type": "LONG",
                "quantity": Decimal("100")
            },
            {
                "exposure": Decimal("5000"),
                "market_value": Decimal("5000"),
                "position_type": "SHORT",
                "quantity": None  # Missing quantity
            }
        ]
        
        result = calculate_portfolio_exposures(positions)
        
        # Should handle None values gracefully
        assert result["gross_exposure"] == Decimal("5000.00")
        assert result["net_exposure"] == Decimal("5000.00")
    
    def test_string_decimal_conversion(self):
        """Test that string values are converted to Decimal properly."""
        positions = [
            {
                "exposure": "10000.50",  # String instead of Decimal
                "market_value": "10000.50",
                "position_type": "LONG",
                "greeks": {
                    "delta": "0.5",  # String instead of Decimal
                    "gamma": "0.02"
                }
            }
        ]
        
        # Exposure calculation
        result = calculate_portfolio_exposures(positions)
        assert result["gross_exposure"] == Decimal("10000.50")
        
        # Greeks aggregation
        greeks_result = aggregate_portfolio_greeks(positions)
        assert greeks_result["delta"] == Decimal("0.5000")
        assert greeks_result["gamma"] == Decimal("0.0200")
    
    def test_malformed_position_data(self):
        """Test handling of malformed position data."""
        positions = [
            {},  # Empty position
            {"position_type": "INVALID"},  # Invalid position type
            {"exposure": Decimal("1000")},  # Missing position_type
        ]
        
        # Should handle gracefully without crashing
        result = calculate_portfolio_exposures(positions)
        assert result["metadata"]["position_count"] == 3
        
        # Greeks aggregation should skip all
        greeks_result = aggregate_portfolio_greeks(positions)
        assert greeks_result["metadata"]["positions_without_greeks"] == 3
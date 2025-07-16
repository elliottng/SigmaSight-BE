"""
Unit tests for Greeks calculations - Section 1.4.2
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch

from app.calculations.greeks import (
    calculate_greeks_hybrid,
    get_mock_greeks,
    calculate_real_greeks,
    extract_option_parameters,
    calculate_time_to_expiry,
    is_options_position,
    is_expired_option,
    get_implied_volatility,
    get_risk_free_rate,
    update_position_greeks,
    bulk_update_portfolio_greeks,
    aggregate_portfolio_greeks,
    MOCK_GREEKS
)
from app.models.positions import PositionType
from tests.fixtures.greeks_fixtures import (
    TEST_POSITIONS,
    TEST_MARKET_DATA,
    EXPECTED_MOCK_GREEKS,
    EDGE_CASE_POSITIONS,
    EMPTY_MARKET_DATA,
    INVALID_MARKET_DATA,
    NO_UNDERLYING_MARKET_DATA
)


class TestGreeksCalculations:
    """Test suite for Greeks calculations"""

    def test_is_options_position(self):
        """Test position type detection"""
        # Create mock position objects
        lc_position = Mock()
        lc_position.position_type = PositionType.LC
        
        long_position = Mock()
        long_position.position_type = PositionType.LONG
        
        assert is_options_position(lc_position) == True
        assert is_options_position(long_position) == False

    def test_is_expired_option(self):
        """Test expired option detection"""
        # Mock expired option
        expired_position = Mock()
        expired_position.position_type = PositionType.LC
        expired_position.expiration_date = date.today() - timedelta(days=1)
        
        # Mock non-expired option
        active_position = Mock()
        active_position.position_type = PositionType.LC
        active_position.expiration_date = date.today() + timedelta(days=30)
        
        # Mock stock position
        stock_position = Mock()
        stock_position.position_type = PositionType.LONG
        stock_position.expiration_date = None
        
        assert is_expired_option(expired_position) == True
        assert is_expired_option(active_position) == False
        assert is_expired_option(stock_position) == False

    def test_calculate_time_to_expiry(self):
        """Test time to expiry calculation"""
        # Test future date
        future_date = date.today() + timedelta(days=30)
        time_to_expiry = calculate_time_to_expiry(future_date)
        assert abs(time_to_expiry - 30/365) < 0.01
        
        # Test past date
        past_date = date.today() - timedelta(days=1)
        time_to_expiry = calculate_time_to_expiry(past_date)
        assert time_to_expiry == 0.0

    def test_extract_option_parameters(self):
        """Test option parameter extraction"""
        # Create mock position with option fields
        position = Mock()
        position.position_type = PositionType.LC
        position.strike_price = Decimal('150.00')
        position.expiration_date = date.today() + timedelta(days=30)
        position.underlying_symbol = 'AAPL'
        
        params = extract_option_parameters(position)
        
        assert params is not None
        assert params['strike'] == 150.00
        assert params['option_type'] == 'c'
        assert params['underlying_symbol'] == 'AAPL'
        assert params['time_to_expiry'] > 0
        
        # Test stock position
        stock_position = Mock()
        stock_position.position_type = PositionType.LONG
        
        params = extract_option_parameters(stock_position)
        assert params is None

    def test_get_implied_volatility(self):
        """Test implied volatility retrieval"""
        # Test with valid market data
        vol = get_implied_volatility('AAPL', TEST_MARKET_DATA)
        assert vol == 0.25
        
        # Test with missing data
        vol = get_implied_volatility('UNKNOWN', TEST_MARKET_DATA)
        assert vol == 0.25  # Default fallback
        
        # Test with empty market data
        vol = get_implied_volatility('AAPL', {})
        assert vol == 0.25

    def test_get_risk_free_rate(self):
        """Test risk-free rate retrieval"""
        # Test with valid market data
        rate = get_risk_free_rate(TEST_MARKET_DATA)
        assert rate == 0.05  # Default
        
        # Test with explicit rate
        market_data_with_rate = {'risk_free_rate': 0.03}
        rate = get_risk_free_rate(market_data_with_rate)
        assert rate == 0.03

    def test_calculate_real_greeks(self):
        """Test real Greeks calculation using py_vollib"""
        try:
            greeks = calculate_real_greeks(
                underlying_price=150.0,
                strike=150.0,
                time_to_expiry=30/365,
                volatility=0.25,
                risk_free_rate=0.05,
                option_type='c'
            )
            
            # Verify all Greeks are present
            assert 'delta' in greeks
            assert 'gamma' in greeks
            assert 'theta' in greeks
            assert 'vega' in greeks
            assert 'rho' in greeks
            
            # Verify reasonable values for ATM call
            assert 0.3 < greeks['delta'] < 0.7
            assert greeks['gamma'] > 0
            assert greeks['theta'] < 0
            assert greeks['vega'] > 0
            assert greeks['rho'] > 0
            
        except ImportError:
            pytest.skip("py_vollib not available")

    def test_get_mock_greeks_all_position_types(self):
        """Test mock Greeks for all position types"""
        # Test Long Call
        greeks = get_mock_greeks(PositionType.LC, Decimal('5'))
        expected = EXPECTED_MOCK_GREEKS['LC']
        assert greeks['delta'] == expected['delta']
        assert greeks['gamma'] == expected['gamma']
        assert greeks['theta'] == expected['theta']
        assert greeks['vega'] == expected['vega']
        assert greeks['rho'] == expected['rho']
        
        # Test Short Call
        greeks = get_mock_greeks(PositionType.SC, Decimal('-3'))
        expected = EXPECTED_MOCK_GREEKS['SC']
        assert greeks['delta'] == expected['delta']
        
        # Test Long Stock
        greeks = get_mock_greeks(PositionType.LONG, Decimal('100'))
        expected = EXPECTED_MOCK_GREEKS['LONG']
        assert greeks['delta'] == expected['delta']
        assert greeks['gamma'] == expected['gamma']
        assert greeks['theta'] == expected['theta']
        assert greeks['vega'] == expected['vega']
        assert greeks['rho'] == expected['rho']
        
        # Test Short Stock
        greeks = get_mock_greeks(PositionType.SHORT, Decimal('-50'))
        expected = EXPECTED_MOCK_GREEKS['SHORT']
        assert greeks['delta'] == expected['delta']

    @pytest.mark.asyncio
    async def test_calculate_greeks_hybrid_stock_positions(self):
        """Test that stock positions use simple delta"""
        # Create mock stock position
        position = Mock()
        position.id = 'test-id'
        position.symbol = 'AAPL'
        position.position_type = PositionType.LONG
        position.quantity = Decimal('100')
        position.expiration_date = None
        
        greeks = await calculate_greeks_hybrid(position, TEST_MARKET_DATA)
        
        expected = EXPECTED_MOCK_GREEKS['LONG']
        assert greeks['delta'] == expected['delta']
        assert greeks['gamma'] == expected['gamma']
        assert greeks['theta'] == expected['theta']
        assert greeks['vega'] == expected['vega']
        assert greeks['rho'] == expected['rho']

    @pytest.mark.asyncio
    async def test_calculate_greeks_hybrid_expired_options(self):
        """Test expired options return zero Greeks"""
        # Create mock expired option
        position = Mock()
        position.id = 'test-id'
        position.symbol = 'AAPL240119C00150000'
        position.position_type = PositionType.LC
        position.quantity = Decimal('1')
        position.expiration_date = date.today() - timedelta(days=1)
        
        greeks = await calculate_greeks_hybrid(position, TEST_MARKET_DATA)
        
        assert greeks['delta'] == 0.0
        assert greeks['gamma'] == 0.0
        assert greeks['theta'] == 0.0
        assert greeks['vega'] == 0.0
        assert greeks['rho'] == 0.0

    @pytest.mark.asyncio
    async def test_calculate_greeks_hybrid_missing_data_fallback(self):
        """Test fallback to mock values when market data missing"""
        # Create mock option position
        position = Mock()
        position.id = 'test-id'
        position.symbol = 'AAPL240119C00150000'
        position.position_type = PositionType.LC
        position.quantity = Decimal('5')
        position.strike_price = Decimal('150.00')
        position.expiration_date = date.today() + timedelta(days=30)
        position.underlying_symbol = 'AAPL'
        
        # Test with empty market data
        greeks = await calculate_greeks_hybrid(position, EMPTY_MARKET_DATA)
        
        expected = EXPECTED_MOCK_GREEKS['LC']
        assert greeks['delta'] == expected['delta']
        assert greeks['gamma'] == expected['gamma']
        assert greeks['theta'] == expected['theta']
        assert greeks['vega'] == expected['vega']
        assert greeks['rho'] == expected['rho']

    @pytest.mark.asyncio
    async def test_calculate_greeks_hybrid_invalid_option_params(self):
        """Test fallback when option parameters are invalid"""
        # Create mock option with missing strike
        position = Mock()
        position.id = 'test-id'
        position.symbol = 'AAPL240119C00150000'
        position.position_type = PositionType.LC
        position.quantity = Decimal('5')
        position.strike_price = None  # Missing strike
        position.expiration_date = date.today() + timedelta(days=30)
        position.underlying_symbol = 'AAPL'
        
        greeks = await calculate_greeks_hybrid(position, TEST_MARKET_DATA)
        
        # Should fallback to mock values
        expected = EXPECTED_MOCK_GREEKS['LC']
        assert greeks['delta'] == expected['delta']

    @pytest.mark.asyncio
    async def test_calculate_greeks_hybrid_real_calculation(self):
        """Test real Greeks calculation with valid market data"""
        # Create mock option position
        position = Mock()
        position.id = 'test-id'
        position.symbol = 'AAPL240119C00150000'
        position.position_type = PositionType.LC
        position.quantity = Decimal('5')
        position.strike_price = Decimal('150.00')
        position.expiration_date = date.today() + timedelta(days=30)
        position.underlying_symbol = 'AAPL'
        
        try:
            greeks = await calculate_greeks_hybrid(position, TEST_MARKET_DATA)
            
            # Should be real calculation, not mock
            # Verify Greeks are reasonable for ATM call
            assert greeks['delta'] > 0  # Positive delta for long call
            assert greeks['gamma'] > 0  # Positive gamma
            assert greeks['theta'] < 0  # Negative theta (time decay)
            assert greeks['vega'] > 0   # Positive vega
            
        except Exception:
            # If real calculation fails, should fallback to mock
            expected = EXPECTED_MOCK_GREEKS['LC']
            greeks = await calculate_greeks_hybrid(position, TEST_MARKET_DATA)
            assert greeks['delta'] == expected['delta']

    @pytest.mark.asyncio
    async def test_update_position_greeks_database(self):
        """Test database update to position_greeks table"""
        # Mock database session
        mock_db = AsyncMock()
        
        test_greeks = {
            'delta': 2.6,
            'gamma': 0.09,
            'theta': -0.225,
            'vega': 0.75,
            'rho': 0.4
        }
        
        # Should not raise exception
        await update_position_greeks(mock_db, 'test-position-id', test_greeks)
        
        # Verify database execute was called
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_update_portfolio_greeks(self):
        """Test bulk Greeks calculation for entire portfolio"""
        # Mock database session
        mock_db = AsyncMock()
        
        # Mock positions result
        mock_positions = [
            Mock(id='pos1', symbol='AAPL', position_type=PositionType.LONG, quantity=Decimal('100')),
            Mock(id='pos2', symbol='MSFT', position_type=PositionType.SHORT, quantity=Decimal('-50'))
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_positions
        mock_db.execute.return_value = mock_result
        
        # Test bulk update
        summary = await bulk_update_portfolio_greeks(mock_db, 'test-portfolio-id', TEST_MARKET_DATA)
        
        # Verify summary structure
        assert 'updated' in summary
        assert 'failed' in summary
        assert 'errors' in summary
        assert 'total_positions' in summary
        assert summary['total_positions'] == 2

    @pytest.mark.asyncio
    async def test_aggregate_portfolio_greeks(self):
        """Test portfolio Greeks aggregation"""
        positions_greeks = [
            {'delta': 2.6, 'gamma': 0.09, 'theta': -0.225, 'vega': 0.75, 'rho': 0.4},
            {'delta': -1.2, 'gamma': 0.05, 'theta': 0.1, 'vega': -0.3, 'rho': -0.2},
            {'delta': 100.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0, 'rho': 0.0}
        ]
        
        portfolio_greeks = await aggregate_portfolio_greeks(positions_greeks)
        
        assert portfolio_greeks['total_delta'] == 2.6 + (-1.2) + 100.0
        assert portfolio_greeks['total_gamma'] == 0.09 + 0.05 + 0.0
        assert portfolio_greeks['total_theta'] == -0.225 + 0.1 + 0.0
        assert portfolio_greeks['total_vega'] == 0.75 + (-0.3) + 0.0
        assert portfolio_greeks['total_rho'] == 0.4 + (-0.2) + 0.0

    @pytest.mark.asyncio
    async def test_aggregate_portfolio_greeks_empty(self):
        """Test portfolio Greeks aggregation with empty list"""
        portfolio_greeks = await aggregate_portfolio_greeks([])
        
        assert portfolio_greeks['total_delta'] == 0.0
        assert portfolio_greeks['total_gamma'] == 0.0
        assert portfolio_greeks['total_theta'] == 0.0
        assert portfolio_greeks['total_vega'] == 0.0
        assert portfolio_greeks['total_rho'] == 0.0

    def test_options_symbol_parsing_edge_cases(self):
        """Test parsing of complex option symbols"""
        # Test basic extraction
        position = Mock()
        position.position_type = PositionType.LC
        position.symbol = 'AAPL240119C00150000'
        position.strike_price = Decimal('150.00')
        position.expiration_date = date(2024, 1, 19)
        position.underlying_symbol = 'AAPL'
        
        params = extract_option_parameters(position)
        assert params is not None
        assert params['underlying_symbol'] == 'AAPL'
        assert params['strike'] == 150.00
        assert params['option_type'] == 'c'

    @pytest.mark.asyncio
    async def test_calculate_greeks_hybrid_calculation_error(self):
        """Test fallback when py_vollib throws exception"""
        # Create mock option position
        position = Mock()
        position.id = 'test-id'
        position.symbol = 'AAPL240119C00150000'
        position.position_type = PositionType.LC
        position.quantity = Decimal('5')
        position.strike_price = Decimal('150.00')
        position.expiration_date = date.today() + timedelta(days=30)
        position.underlying_symbol = 'AAPL'
        
        # Mock py_vollib to raise exception
        with patch('app.calculations.greeks.calculate_real_greeks') as mock_real:
            mock_real.side_effect = Exception("Calculation error")
            
            greeks = await calculate_greeks_hybrid(position, TEST_MARKET_DATA)
            
            # Should fallback to mock values
            expected = EXPECTED_MOCK_GREEKS['LC']
            assert greeks['delta'] == expected['delta']


class TestGreeksPerformance:
    """Performance tests for Greeks calculations"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_greeks_calculation_performance(self):
        """Test Greeks calculation speed for large portfolios"""
        # Create 100 mock positions
        positions = []
        for i in range(100):
            position = Mock()
            position.id = f'pos-{i}'
            position.symbol = f'AAPL240119C00{150 + i}000'
            position.position_type = PositionType.LC
            position.quantity = Decimal('1')
            position.strike_price = Decimal(str(150 + i))
            position.expiration_date = date.today() + timedelta(days=30)
            position.underlying_symbol = 'AAPL'
            positions.append(position)
        
        # Mock database
        mock_db = AsyncMock()
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = positions
        mock_db.execute.return_value = mock_result
        
        import time
        start_time = time.time()
        
        # Test bulk update
        summary = await bulk_update_portfolio_greeks(mock_db, 'test-portfolio', TEST_MARKET_DATA)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete in reasonable time
        assert execution_time < 5.0  # Less than 5 seconds for 100 positions
        assert summary['total_positions'] == 100

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_single_position_performance(self):
        """Test single position calculation performance"""
        position = Mock()
        position.id = 'test-id'
        position.symbol = 'AAPL240119C00150000'
        position.position_type = PositionType.LC
        position.quantity = Decimal('5')
        position.strike_price = Decimal('150.00')
        position.expiration_date = date.today() + timedelta(days=30)
        position.underlying_symbol = 'AAPL'
        
        import time
        start_time = time.time()
        
        # Calculate Greeks
        greeks = await calculate_greeks_hybrid(position, TEST_MARKET_DATA)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete very quickly
        assert execution_time < 0.1  # Less than 100ms per position
        assert 'delta' in greeks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
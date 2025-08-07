"""
Test fixtures for Greeks calculations
"""
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from app.models.positions import PositionType

# Market data includes dividend yield
TEST_MARKET_DATA = {
    'AAPL': {
        'current_price': 150.00,
        'implied_volatility': 0.25,  # 25% - fallback if missing
        'risk_free_rate': 0.05,      # 5%
        'dividend_yield': 0.0        # 0% default
    },
    'MSFT': {
        'current_price': 380.00,
        'implied_volatility': 0.22,
        'risk_free_rate': 0.05,
        'dividend_yield': 0.0
    }
}

# Test positions for all position types
# Position structure matches SQLAlchemy model fields
TEST_POSITIONS = {
    'LC': {  # Long Call
        'id': uuid4(),
        'portfolio_id': uuid4(),
        'symbol': 'AAPL240119C00150000',
        'position_type': PositionType.LC,
        'quantity': Decimal('5'),
        'entry_price': Decimal('3.50'),
        'entry_date': date(2024, 1, 1),
        'last_price': Decimal('4.00'),
        'market_value': Decimal('2000.00'),
        'unrealized_pnl': Decimal('250.00'),
        # Option-specific fields
        'underlying_symbol': 'AAPL',
        'strike_price': Decimal('150.00'),
        'expiration_date': date(2024, 1, 19)
    },
    'SC': {  # Short Call
        'id': uuid4(),
        'portfolio_id': uuid4(),
        'symbol': 'AAPL240119C00155000',
        'position_type': PositionType.SC,
        'quantity': Decimal('-3'),
        'entry_price': Decimal('2.00'),
        'entry_date': date(2024, 1, 1),
        'last_price': Decimal('1.50'),
        'market_value': Decimal('450.00'),
        'unrealized_pnl': Decimal('150.00'),
        'underlying_symbol': 'AAPL',
        'strike_price': Decimal('155.00'),
        'expiration_date': date(2024, 1, 19)
    },
    'LP': {  # Long Put
        'id': uuid4(),
        'portfolio_id': uuid4(),
        'symbol': 'AAPL240119P00145000',
        'position_type': PositionType.LP,
        'quantity': Decimal('2'),
        'entry_price': Decimal('3.00'),
        'entry_date': date(2024, 1, 1),
        'last_price': Decimal('2.50'),
        'market_value': Decimal('500.00'),
        'unrealized_pnl': Decimal('-100.00'),
        'underlying_symbol': 'AAPL',
        'strike_price': Decimal('145.00'),
        'expiration_date': date(2024, 1, 19)
    },
    'SP': {  # Short Put
        'id': uuid4(),
        'portfolio_id': uuid4(),
        'symbol': 'AAPL240119P00140000',
        'position_type': PositionType.SP,
        'quantity': Decimal('-4'),
        'entry_price': Decimal('1.00'),
        'entry_date': date(2024, 1, 1),
        'last_price': Decimal('0.75'),
        'market_value': Decimal('300.00'),
        'unrealized_pnl': Decimal('100.00'),
        'underlying_symbol': 'AAPL',
        'strike_price': Decimal('140.00'),
        'expiration_date': date(2024, 1, 19)
    },
    'LONG': {  # Long Stock
        'id': uuid4(),
        'portfolio_id': uuid4(),
        'symbol': 'AAPL',
        'position_type': PositionType.LONG,
        'quantity': Decimal('100'),
        'entry_price': Decimal('145.00'),
        'entry_date': date(2024, 1, 1),
        'last_price': Decimal('150.00'),
        'market_value': Decimal('15000.00'),
        'unrealized_pnl': Decimal('500.00'),
        'underlying_symbol': 'AAPL',
        'strike_price': None,
        'expiration_date': None
    },
    'SHORT': {  # Short Stock
        'id': uuid4(),
        'portfolio_id': uuid4(),
        'symbol': 'MSFT',
        'position_type': PositionType.SHORT,
        'quantity': Decimal('-50'),
        'entry_price': Decimal('385.00'),
        'entry_date': date(2024, 1, 1),
        'last_price': Decimal('380.00'),
        'market_value': Decimal('19000.00'),
        'unrealized_pnl': Decimal('250.00'),
        'underlying_symbol': 'MSFT',
        'strike_price': None,
        'expiration_date': None
    },
    'EXPIRED': {  # Expired Option
        'id': uuid4(),
        'portfolio_id': uuid4(),
        'symbol': 'AAPL231215C00150000',
        'position_type': PositionType.LC,
        'quantity': Decimal('1'),
        'entry_price': Decimal('2.00'),
        'entry_date': date(2023, 12, 1),
        'last_price': Decimal('0.00'),
        'market_value': Decimal('0.00'),
        'unrealized_pnl': Decimal('-200.00'),
        'underlying_symbol': 'AAPL',
        'strike_price': Decimal('150.00'),
        'expiration_date': date(2023, 12, 15)  # Past date
    }
}

# Expected real calculation results (approximate)
# Long Call (AAPL, strike=150, 30 days, vol=25%)
EXPECTED_REAL_GREEKS = {
    'LC': {
        'delta': 0.52 * 5,           # 5 contracts
        'gamma': 0.018 * 5,
        'theta': -0.045 * 5,         # Already daily (÷365)
        'vega': 0.12 * 5,            # Already per 1% (÷100)
        'rho': 0.06 * 5
    }
}


# Test cases for edge cases
EDGE_CASE_POSITIONS = {
    'MISSING_STRIKE': {
        'id': uuid4(),
        'portfolio_id': uuid4(),
        'symbol': 'AAPL240119C00150000',
        'position_type': PositionType.LC,
        'quantity': Decimal('1'),
        'entry_price': Decimal('3.50'),
        'entry_date': date(2024, 1, 1),
        'underlying_symbol': 'AAPL',
        'strike_price': None,  # Missing strike
        'expiration_date': date(2024, 1, 19)
    },
    'MISSING_EXPIRY': {
        'id': uuid4(),
        'portfolio_id': uuid4(),
        'symbol': 'AAPL240119C00150000',
        'position_type': PositionType.LC,
        'quantity': Decimal('1'),
        'entry_price': Decimal('3.50'),
        'entry_date': date(2024, 1, 1),
        'underlying_symbol': 'AAPL',
        'strike_price': Decimal('150.00'),
        'expiration_date': None  # Missing expiry
    },
    'MISSING_UNDERLYING': {
        'id': uuid4(),
        'portfolio_id': uuid4(),
        'symbol': 'AAPL240119C00150000',
        'position_type': PositionType.LC,
        'quantity': Decimal('1'),
        'entry_price': Decimal('3.50'),
        'entry_date': date(2024, 1, 1),
        'underlying_symbol': None,  # Missing underlying
        'strike_price': Decimal('150.00'),
        'expiration_date': date(2024, 1, 19)
    }
}

# Market data scenarios
EMPTY_MARKET_DATA = {}

INVALID_MARKET_DATA = {
    'AAPL': {
        'invalid_field': 'test'
        # Missing current_price
    }
}

NO_UNDERLYING_MARKET_DATA = {
    'MSFT': {
        'current_price': 380.00,
        'implied_volatility': 0.22
    }
    # Missing AAPL data
}
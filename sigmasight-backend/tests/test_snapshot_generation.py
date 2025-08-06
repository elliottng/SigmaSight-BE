"""
Unit tests for portfolio snapshot generation
"""
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from unittest.mock import Mock, patch, AsyncMock

from app.calculations.snapshots import (
    create_portfolio_snapshot,
    _fetch_active_positions,
    _calculate_pnl,
    _count_positions
)
from app.models.positions import Position, PositionType
from app.models.snapshots import PortfolioSnapshot
from app.models.market_data import PositionGreeks


class TestSnapshotGeneration:
    """Test suite for portfolio snapshot generation"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        db = AsyncMock()
        db.commit = AsyncMock()
        db.rollback = AsyncMock()
        return db
    
    @pytest.fixture
    def sample_portfolio_id(self):
        """Sample portfolio ID"""
        return uuid4()
    
    @pytest.fixture
    def sample_positions(self, sample_portfolio_id):
        """Sample positions for testing"""
        positions = [
            Position(
                id=uuid4(),
                portfolio_id=sample_portfolio_id,
                symbol="AAPL",
                position_type=PositionType.LONG,
                quantity=Decimal("100"),
                entry_price=Decimal("150.00"),
                entry_date=date(2025, 1, 1),
                last_price=Decimal("155.00"),
                market_value=Decimal("15500.00")
            ),
            Position(
                id=uuid4(),
                portfolio_id=sample_portfolio_id,
                symbol="GOOGL",
                position_type=PositionType.SHORT,
                quantity=Decimal("-50"),
                entry_price=Decimal("2800.00"),
                entry_date=date(2025, 1, 1),
                last_price=Decimal("2850.00"),
                market_value=Decimal("-142500.00")
            ),
            Position(
                id=uuid4(),
                portfolio_id=sample_portfolio_id,
                symbol="AAPL_240119C150",
                position_type=PositionType.LC,
                quantity=Decimal("10"),
                entry_price=Decimal("5.00"),
                entry_date=date(2025, 1, 1),
                strike_price=Decimal("150.00"),
                expiration_date=date(2025, 1, 19),
                last_price=Decimal("7.50"),
                market_value=Decimal("7500.00")
            )
        ]
        return positions
    
    @pytest.fixture
    def sample_greeks(self):
        """Sample Greeks data"""
        return {
            "delta": Decimal("0.60"),
            "gamma": Decimal("0.02"),
            "theta": Decimal("-0.05"),
            "vega": Decimal("0.15"),
            "rho": Decimal("0.08")
        }
    
    @pytest.mark.asyncio
    async def test_create_portfolio_snapshot_success(self, mock_db, sample_portfolio_id, sample_positions):
        """Test successful snapshot creation"""
        calculation_date = date(2025, 1, 15)
        
        # Mock trading day check
        with patch('app.calculations.snapshots.trading_calendar.is_trading_day', return_value=True):
            # Mock position fetching
            with patch('app.calculations.snapshots._fetch_active_positions', 
                      return_value=sample_positions) as mock_fetch:
                
                # Mock position data preparation
                # Note: exposure must be signed (negative for shorts)
                position_data = {
                    "positions": [
                        {
                            "id": pos.id,
                            "symbol": pos.symbol,
                            "quantity": pos.quantity,
                            "market_value": abs(pos.market_value),  # Always positive
                            "exposure": pos.market_value if pos.quantity > 0 else -abs(pos.market_value),  # Signed
                            "position_type": pos.position_type,
                            "greeks": None
                        } for pos in sample_positions
                    ],
                    "warnings": []
                }
                
                with patch('app.calculations.snapshots._prepare_position_data',
                          return_value=position_data):
                    
                    # Mock PnL calculation
                    pnl_data = {
                        "daily_pnl": Decimal("500.00"),
                        "daily_return": Decimal("0.0033"),
                        "cumulative_pnl": Decimal("2500.00")
                    }
                    
                    with patch('app.calculations.snapshots._calculate_pnl',
                              return_value=pnl_data):
                        
                        # Mock snapshot creation
                        mock_snapshot = Mock(spec=PortfolioSnapshot)
                        with patch('app.calculations.snapshots._create_or_update_snapshot',
                                  return_value=mock_snapshot):
                            
                            result = await create_portfolio_snapshot(
                                db=mock_db,
                                portfolio_id=sample_portfolio_id,
                                calculation_date=calculation_date
                            )
        
        assert result["success"] is True
        assert "Snapshot created successfully" in result["message"]
        assert result["snapshot"] is not None
        assert result["statistics"]["positions_processed"] == 3
    
    @pytest.mark.asyncio
    async def test_create_portfolio_snapshot_non_trading_day(self, mock_db, sample_portfolio_id):
        """Test snapshot creation on non-trading day"""
        calculation_date = date(2025, 1, 18)  # Saturday
        
        # Mock trading day check to return False
        with patch('app.calculations.snapshots.trading_calendar.is_trading_day', return_value=False):
            result = await create_portfolio_snapshot(
                db=mock_db,
                portfolio_id=sample_portfolio_id,
                calculation_date=calculation_date
            )
        
        assert result["success"] is False
        assert "not a trading day" in result["message"]
        assert result["snapshot"] is None
    
    @pytest.mark.asyncio
    async def test_create_portfolio_snapshot_no_positions(self, mock_db, sample_portfolio_id):
        """Test snapshot creation with no active positions"""
        calculation_date = date(2025, 1, 15)
        
        with patch('app.calculations.snapshots.trading_calendar.is_trading_day', return_value=True):
            with patch('app.calculations.snapshots._fetch_active_positions', 
                      return_value=[]):
                
                # Mock zero snapshot creation
                mock_snapshot = Mock(spec=PortfolioSnapshot)
                with patch('app.calculations.snapshots._create_zero_snapshot',
                          return_value=mock_snapshot):
                    
                    result = await create_portfolio_snapshot(
                        db=mock_db,
                        portfolio_id=sample_portfolio_id,
                        calculation_date=calculation_date
                    )
        
        assert result["success"] is True
        assert "zero snapshot" in result["message"]
        assert result["snapshot"] is not None
    
    def test_count_positions(self, sample_positions):
        """Test position counting logic"""
        counts = _count_positions(sample_positions)
        
        assert counts["total"] == 3
        assert counts["long"] == 2  # AAPL stock and AAPL call
        assert counts["short"] == 1  # GOOGL short
    
    @pytest.mark.asyncio
    async def test_calculate_pnl_first_snapshot(self, mock_db, sample_portfolio_id):
        """Test P&L calculation for first snapshot"""
        calculation_date = date(2025, 1, 15)
        current_value = Decimal("150000.00")
        
        # Mock no previous trading day
        with patch('app.calculations.snapshots.trading_calendar.get_previous_trading_day',
                  return_value=None):
            
            pnl_data = await _calculate_pnl(
                db=mock_db,
                portfolio_id=sample_portfolio_id,
                calculation_date=calculation_date,
                current_value=current_value
            )
        
        assert pnl_data["daily_pnl"] == Decimal('0')
        assert pnl_data["daily_return"] == Decimal('0')
        assert pnl_data["cumulative_pnl"] == Decimal('0')
    
    @pytest.mark.asyncio
    async def test_calculate_pnl_with_previous_snapshot(self, mock_db, sample_portfolio_id):
        """Test P&L calculation with previous snapshot"""
        calculation_date = date(2025, 1, 15)
        current_value = Decimal("152000.00")
        
        # Mock previous snapshot
        previous_snapshot = Mock(spec=PortfolioSnapshot)
        previous_snapshot.total_value = Decimal("150000.00")
        previous_snapshot.cumulative_pnl = Decimal("5000.00")
        
        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=previous_snapshot)
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        with patch('app.calculations.snapshots.trading_calendar.get_previous_trading_day',
                  return_value=date(2025, 1, 14)):
            
            pnl_data = await _calculate_pnl(
                db=mock_db,
                portfolio_id=sample_portfolio_id,
                calculation_date=calculation_date,
                current_value=current_value
            )
        
        assert pnl_data["daily_pnl"] == Decimal("2000.00")
        assert pnl_data["daily_return"] == Decimal("0.013333")  # 2000/150000
        assert pnl_data["cumulative_pnl"] == Decimal("7000.00")  # 5000 + 2000
    
    @pytest.mark.asyncio
    async def test_fetch_active_positions(self, mock_db, sample_portfolio_id, sample_positions):
        """Test fetching active positions"""
        calculation_date = date(2025, 1, 15)
        
        # Mock database query result
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=Mock(all=Mock(return_value=sample_positions)))
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        positions = await _fetch_active_positions(
            db=mock_db,
            portfolio_id=sample_portfolio_id,
            calculation_date=calculation_date
        )
        
        assert len(positions) == 3
        assert all(isinstance(pos, Position) for pos in positions)
    
    @pytest.mark.asyncio
    async def test_create_portfolio_snapshot_with_warnings(self, mock_db, sample_portfolio_id, sample_positions):
        """Test snapshot creation with warnings for missing data"""
        calculation_date = date(2025, 1, 15)
        
        with patch('app.calculations.snapshots.trading_calendar.is_trading_day', return_value=True):
            with patch('app.calculations.snapshots._fetch_active_positions', 
                      return_value=sample_positions):
                
                # Mock position data with warnings
                position_data = {
                    "positions": [
                        {
                            "id": pos.id,
                            "symbol": pos.symbol,
                            "quantity": pos.quantity,
                            "market_value": abs(pos.market_value),  # Always positive
                            "exposure": pos.market_value if pos.quantity > 0 else -abs(pos.market_value),  # Signed
                            "position_type": pos.position_type,
                            "greeks": None
                        } for pos in sample_positions
                    ],
                    "warnings": ["Missing Greeks for options position AAPL_240119C150"]
                }
                
                with patch('app.calculations.snapshots._prepare_position_data',
                          return_value=position_data):
                    
                    # Mock other required patches
                    with patch('app.calculations.snapshots._calculate_pnl',
                              return_value={"daily_pnl": Decimal("0"), "daily_return": Decimal("0"), 
                                          "cumulative_pnl": Decimal("0")}):
                        
                        with patch('app.calculations.snapshots._create_or_update_snapshot',
                                  return_value=Mock(spec=PortfolioSnapshot)):
                            
                            result = await create_portfolio_snapshot(
                                db=mock_db,
                                portfolio_id=sample_portfolio_id,
                                calculation_date=calculation_date
                            )
        
        assert result["success"] is True
        assert len(result["statistics"]["warnings"]) == 1
        assert "Missing Greeks" in result["statistics"]["warnings"][0]
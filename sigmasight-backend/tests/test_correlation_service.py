"""
Unit tests for CorrelationService
"""

import pytest
import pandas as pd
import numpy as np
from decimal import Decimal
from datetime import datetime, date, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.correlation_service import CorrelationService
from app.models import Position, Portfolio, PositionType


class TestCorrelationService:
    """Test cases for CorrelationService"""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        mock_db = AsyncMock()
        return mock_db
    
    @pytest.fixture
    def correlation_service(self, mock_db):
        """Create CorrelationService instance"""
        return CorrelationService(mock_db)
    
    @pytest.fixture
    def sample_positions(self):
        """Create sample positions for testing"""
        positions = []
        
        # Create positions with different values and weights
        position_data = [
            ("AAPL", 100, Decimal("150.00"), PositionType.LONG),
            ("MSFT", 50, Decimal("200.00"), PositionType.LONG),
            ("GOOGL", 20, Decimal("100.00"), PositionType.LONG),
            ("TSLA", -30, Decimal("300.00"), PositionType.SHORT),
            ("NVDA", 10, Decimal("500.00"), PositionType.LONG),
        ]
        
        for symbol, quantity, price, pos_type in position_data:
            position = Position(
                id=uuid4(),
                symbol=symbol,
                quantity=quantity,
                last_price=price,
                position_type=pos_type
            )
            positions.append(position)
        
        return positions
    
    def test_filter_significant_positions_both_mode(self, correlation_service, sample_positions):
        """Test position filtering with 'both' mode"""
        # Total portfolio value: 15000 + 10000 + 2000 + 9000 + 5000 = 41000
        portfolio_value = Decimal("41000")
        
        
        # Filter: min_value=10000, min_weight=0.25 (10250), mode='both'
        filtered = correlation_service.filter_significant_positions(
            sample_positions,
            portfolio_value,
            min_value=Decimal("10000"),
            min_weight=Decimal("0.25"),  # 25% = 10250
            filter_mode="both"
        )
        
        # Only AAPL (15000, 36.6%) meets both criteria
        # MSFT (10000, 24.4%) meets value but not weight
        # TSLA (9000, 22.0%) meets neither
        assert len(filtered) == 1
        symbols = {p.symbol for p in filtered}
        assert symbols == {"AAPL"}
    
    def test_filter_significant_positions_value_only(self, correlation_service, sample_positions):
        """Test position filtering with 'value_only' mode"""
        portfolio_value = Decimal("41000")
        
        filtered = correlation_service.filter_significant_positions(
            sample_positions,
            portfolio_value,
            min_value=Decimal("5000"),
            min_weight=Decimal("0.15"),
            filter_mode="value_only"
        )
        
        # AAPL (15000), MSFT (10000), TSLA (9000), NVDA (5000) all meet value criteria
        assert len(filtered) == 4
        symbols = {p.symbol for p in filtered}
        assert symbols == {"AAPL", "MSFT", "TSLA", "NVDA"}
    
    def test_filter_significant_positions_either_mode(self, correlation_service, sample_positions):
        """Test position filtering with 'either' mode"""
        portfolio_value = Decimal("41000")
        
        filtered = correlation_service.filter_significant_positions(
            sample_positions,
            portfolio_value,
            min_value=Decimal("20000"),  # Only AAPL (15000) fails this
            min_weight=Decimal("0.35"),   # Only AAPL (36.6%) meets this
            filter_mode="either"
        )
        
        # Only AAPL meets either criteria (weight threshold)
        assert len(filtered) == 1
        assert filtered[0].symbol == "AAPL"
    
    def test_calculate_pairwise_correlations(self, correlation_service):
        """Test pairwise correlation calculation"""
        # Create sample returns data
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        
        # Create correlated returns
        np.random.seed(42)
        base_returns = np.random.normal(0, 0.02, 30)
        
        returns_data = {
            'AAPL': base_returns + np.random.normal(0, 0.01, 30),
            'MSFT': base_returns + np.random.normal(0, 0.01, 30),
            'GOOGL': np.random.normal(0, 0.02, 30)  # Uncorrelated
        }
        
        returns_df = pd.DataFrame(returns_data, index=dates)
        
        # Calculate correlations
        correlation_matrix = correlation_service.calculate_pairwise_correlations(returns_df)
        
        # Verify matrix properties
        assert correlation_matrix.shape == (3, 3)
        assert np.allclose(np.diag(correlation_matrix), 1.0)  # Diagonal should be 1
        assert correlation_matrix.loc['AAPL', 'MSFT'] == correlation_matrix.loc['MSFT', 'AAPL']  # Symmetric
        
        # AAPL and MSFT should be more correlated than either with GOOGL
        aapl_msft_corr = abs(correlation_matrix.loc['AAPL', 'MSFT'])
        aapl_googl_corr = abs(correlation_matrix.loc['AAPL', 'GOOGL'])
        assert aapl_msft_corr > aapl_googl_corr
    
    @pytest.mark.asyncio
    async def test_detect_correlation_clusters_single_cluster(self, correlation_service, sample_positions):
        """Test cluster detection with high correlations"""
        # Create correlation matrix with one clear cluster
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        correlation_data = [
            [1.0, 0.8, 0.3],
            [0.8, 1.0, 0.2],
            [0.3, 0.2, 1.0]
        ]
        correlation_matrix = pd.DataFrame(correlation_data, index=symbols, columns=symbols)
        
        # Create corresponding positions
        positions = sample_positions[:3]  # AAPL, MSFT, GOOGL
        portfolio_value = Decimal("27000")  # 15000 + 10000 + 2000
        
        # Mock database calls for nickname generation
        with patch.object(correlation_service, 'generate_cluster_nickname', return_value="Tech Cluster") as mock_nickname:
            # Detect clusters with threshold 0.7
            clusters = await correlation_service.detect_correlation_clusters(
                correlation_matrix, positions, portfolio_value, threshold=0.7
            )
        
        # Should find one cluster with AAPL and MSFT
        assert len(clusters) == 1
        cluster = clusters[0]
        assert set(cluster["symbols"]) == {"AAPL", "MSFT"}
        assert cluster["avg_correlation"] > Decimal("0.7")
    
    @pytest.mark.asyncio
    async def test_detect_correlation_clusters_no_clusters(self, correlation_service, sample_positions):
        """Test cluster detection with low correlations"""
        # Create correlation matrix with no high correlations
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        correlation_data = [
            [1.0, 0.3, 0.2],
            [0.3, 1.0, 0.1],
            [0.2, 0.1, 1.0]
        ]
        correlation_matrix = pd.DataFrame(correlation_data, index=symbols, columns=symbols)
        
        positions = sample_positions[:3]
        portfolio_value = Decimal("27000")
        
        # Mock database calls for nickname generation (won't be called)
        with patch.object(correlation_service, 'generate_cluster_nickname', return_value="No Cluster") as mock_nickname:
            # Detect clusters with threshold 0.7
            clusters = await correlation_service.detect_correlation_clusters(
                correlation_matrix, positions, portfolio_value, threshold=0.7
            )
        
        # Should find no clusters
        assert len(clusters) == 0
    
    def test_calculate_portfolio_metrics(self, correlation_service, sample_positions):
        """Test portfolio-level metrics calculation"""
        # Create correlation matrix
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        correlation_data = [
            [1.0, 0.8, 0.3],
            [0.8, 1.0, 0.2],
            [0.3, 0.2, 1.0]
        ]
        correlation_matrix = pd.DataFrame(correlation_data, index=symbols, columns=symbols)
        
        # Create cluster with AAPL and MSFT
        clusters = [{
            "symbols": ["AAPL", "MSFT"],
            "avg_correlation": Decimal("0.8")
        }]
        
        positions = sample_positions[:3]
        
        metrics = correlation_service.calculate_portfolio_metrics(
            correlation_matrix, positions, clusters
        )
        
        # Verify metrics
        assert "overall_correlation" in metrics
        assert "concentration_score" in metrics
        assert "effective_positions" in metrics
        assert "data_quality" in metrics
        
        assert metrics["overall_correlation"] > Decimal("0")
        assert metrics["concentration_score"] >= Decimal("0")
        assert metrics["effective_positions"] > Decimal("0")
        assert metrics["data_quality"] == "sufficient"
    
    def test_validate_data_sufficiency(self, correlation_service):
        """Test data sufficiency validation"""
        # Create returns DataFrame with varying data availability
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        
        returns_data = {
            'AAPL': [0.01] * 25 + [np.nan] * 5,  # 25 valid days
            'MSFT': [0.02] * 15 + [np.nan] * 15, # 15 valid days
            'GOOGL': [np.nan] * 10 + [0.03] * 20  # 20 valid days
        }
        
        returns_df = pd.DataFrame(returns_data, index=dates)
        
        # Validate with min_days=20
        valid_positions = correlation_service._validate_data_sufficiency(returns_df, min_days=20)
        
        # Only AAPL (25 days) and GOOGL (20 days) should be valid
        assert set(valid_positions) == {"AAPL", "GOOGL"}
    
    @pytest.mark.asyncio
    async def test_generate_cluster_nickname_tags(self, correlation_service, mock_db):
        """Test cluster nickname generation using tags"""
        # Mock tag query result
        mock_tag = MagicMock()
        mock_tag.name = "Tech Stocks"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_tag, mock_tag]  # Two occurrences
        mock_db.execute.return_value = mock_result
        
        # Create sample positions
        positions = [
            MagicMock(id=uuid4(), symbol="AAPL"),
            MagicMock(id=uuid4(), symbol="MSFT")
        ]
        
        nickname = await correlation_service.generate_cluster_nickname(
            ["AAPL", "MSFT"], positions
        )
        
        assert nickname == "Tech Stocks"
    
    @pytest.mark.asyncio
    async def test_generate_cluster_nickname_fallback(self, correlation_service, mock_db):
        """Test cluster nickname fallback to largest position"""
        # Mock empty tag query result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        
        # Mock empty sector query result
        mock_result2 = MagicMock()
        mock_result2.scalar_one_or_none.return_value = None
        
        mock_db.execute.side_effect = [mock_result, mock_result2, mock_result2]
        
        # Create sample positions with different values
        positions = [
            MagicMock(id=uuid4(), symbol="AAPL", quantity=100, last_price=Decimal("150")),
            MagicMock(id=uuid4(), symbol="MSFT", quantity=50, last_price=Decimal("200"))
        ]
        
        nickname = await correlation_service.generate_cluster_nickname(
            ["AAPL", "MSFT"], positions
        )
        
        # Should use AAPL (larger position: 15000 vs 10000)
        assert nickname == "AAPL lookalikes"


@pytest.mark.asyncio
class TestCorrelationServiceIntegration:
    """Integration tests requiring database"""
    
    async def test_full_correlation_calculation_flow(self):
        """Test the complete correlation calculation flow"""
        # This would require a test database setup
        # For now, we'll mark it as a placeholder
        pass
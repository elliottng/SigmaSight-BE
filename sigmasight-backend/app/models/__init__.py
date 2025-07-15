"""
SQLAlchemy models for SigmaSight Backend
"""

# Import all models to ensure they are registered with SQLAlchemy
from app.models.users import User, Portfolio
from app.models.positions import Position, Tag, PositionType, TagType, position_tags
from app.models.market_data import MarketDataCache, PositionGreeks, FactorDefinition, FactorExposure
from app.models.snapshots import PortfolioSnapshot, BatchJob, BatchJobSchedule

# Export all models
__all__ = [
    # Users module
    "User",
    "Portfolio",
    
    # Positions module
    "Position",
    "Tag",
    "PositionType",
    "TagType",
    "position_tags",
    
    # Market data module
    "MarketDataCache",
    "PositionGreeks",
    "FactorDefinition",
    "FactorExposure",
    
    # Snapshots module
    "PortfolioSnapshot",
    "BatchJob",
    "BatchJobSchedule",
]
"""
SQLAlchemy models for SigmaSight Backend
"""

# Import all models to ensure they are registered with SQLAlchemy
from app.models.users import User, Portfolio
from app.models.positions import Position, Tag, PositionType, TagType, position_tags
from app.models.market_data import MarketDataCache, PositionGreeks, FactorDefinition, FactorExposure, PositionFactorExposure
from app.models.snapshots import PortfolioSnapshot, BatchJob, BatchJobSchedule
from app.models.modeling import ModelingSessionSnapshot
from app.models.history import ExportHistory, HistoricalBackfillProgress

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
    "PositionFactorExposure",
    
    # Snapshots module
    "PortfolioSnapshot",
    "BatchJob",
    "BatchJobSchedule",
    
    # Modeling module
    "ModelingSessionSnapshot",
    
    # History module
    "ExportHistory",
    "HistoricalBackfillProgress",
]
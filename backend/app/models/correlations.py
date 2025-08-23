"""
Correlation analysis models for position-to-position correlation tracking
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    Column, String, Integer, DateTime, ForeignKey, 
    UniqueConstraint, Index, DECIMAL, Enum
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class CorrelationCalculation(Base):
    """
    Tracks correlation calculation runs for portfolios with configurable filtering
    """
    __tablename__ = "correlation_calculations"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    portfolio_id = Column(PostgresUUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False)
    duration_days = Column(Integer, nullable=False)
    calculation_date = Column(DateTime(timezone=True), nullable=False)
    
    # Correlation metrics
    overall_correlation = Column(DECIMAL(8, 6), nullable=False)
    correlation_concentration_score = Column(DECIMAL(8, 6), nullable=False)
    effective_positions = Column(DECIMAL(8, 2), nullable=False)
    data_quality = Column(String(20), nullable=False)  # 'sufficient', 'limited', 'insufficient'
    
    # Position filtering configuration (per-portfolio settings)
    min_position_value = Column(DECIMAL(18, 4))
    min_portfolio_weight = Column(DECIMAL(8, 6))
    filter_mode = Column(String(20), default='both')  # 'value_only', 'weight_only', 'both', 'either'
    correlation_threshold = Column(DECIMAL(8, 6), default=0.7)
    
    # Metadata
    positions_included = Column(Integer, nullable=False)
    positions_excluded = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="correlation_calculations")
    clusters = relationship("CorrelationCluster", back_populates="calculation", cascade="all, delete-orphan")
    pairwise_correlations = relationship("PairwiseCorrelation", back_populates="calculation", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('portfolio_id', 'duration_days', 'calculation_date'),
        Index('idx_correlation_calculations_portfolio_date', 'portfolio_id', 'calculation_date'),
    )


class CorrelationCluster(Base):
    """
    Represents a cluster of highly correlated positions
    """
    __tablename__ = "correlation_clusters"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    correlation_calculation_id = Column(PostgresUUID(as_uuid=True), ForeignKey("correlation_calculations.id"), nullable=False)
    cluster_number = Column(Integer, nullable=False)
    nickname = Column(String(100), nullable=False)
    avg_correlation = Column(DECIMAL(8, 6), nullable=False)
    total_value = Column(DECIMAL(18, 4), nullable=False)
    portfolio_percentage = Column(DECIMAL(8, 6), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    calculation = relationship("CorrelationCalculation", back_populates="clusters")
    positions = relationship("CorrelationClusterPosition", back_populates="cluster", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_correlation_clusters_calculation', 'correlation_calculation_id'),
    )


class CorrelationClusterPosition(Base):
    """
    Links positions to their correlation clusters
    """
    __tablename__ = "correlation_cluster_positions"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    cluster_id = Column(PostgresUUID(as_uuid=True), ForeignKey("correlation_clusters.id"), nullable=False)
    position_id = Column(PostgresUUID(as_uuid=True), ForeignKey("positions.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    value = Column(DECIMAL(18, 4), nullable=False)
    portfolio_percentage = Column(DECIMAL(8, 6), nullable=False)
    correlation_to_cluster = Column(DECIMAL(8, 6), nullable=False)
    
    # Relationships
    cluster = relationship("CorrelationCluster", back_populates="positions")
    position = relationship("Position")
    
    __table_args__ = (
        Index('idx_cluster_positions_cluster', 'cluster_id'),
        Index('idx_cluster_positions_position', 'position_id'),
    )


class PairwiseCorrelation(Base):
    """
    Stores pairwise correlations between all positions (including both directions and self-correlations)
    """
    __tablename__ = "pairwise_correlations"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    correlation_calculation_id = Column(PostgresUUID(as_uuid=True), ForeignKey("correlation_calculations.id"), nullable=False)
    symbol_1 = Column(String(20), nullable=False)
    symbol_2 = Column(String(20), nullable=False)
    correlation_value = Column(DECIMAL(8, 6), nullable=False)
    data_points = Column(Integer, nullable=False)
    statistical_significance = Column(DECIMAL(8, 6))
    
    # Relationships
    calculation = relationship("CorrelationCalculation", back_populates="pairwise_correlations")
    
    __table_args__ = (
        Index('idx_pairwise_correlations_calculation_symbols', 'correlation_calculation_id', 'symbol_1', 'symbol_2'),
        Index('idx_pairwise_correlations_calculation', 'correlation_calculation_id'),
    )
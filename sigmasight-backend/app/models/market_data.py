"""
Market data and analytics models
"""
from datetime import datetime, date
from uuid import uuid4
from decimal import Decimal
from sqlalchemy import String, DateTime, ForeignKey, Index, Numeric, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.database import Base


class MarketDataCache(Base):
    """Market data cache - stores historical price data"""
    __tablename__ = "market_data_cache"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    open: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    high: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    low: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    close: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    volume: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Sector/Industry data from YFinance
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    data_source: Mapped[str] = mapped_column(String(20), nullable=False, default='polygon')
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('symbol', 'date', name='uq_market_data_cache_symbol_date'),
        Index('ix_market_data_cache_symbol', 'symbol'),
        Index('ix_market_data_cache_date', 'date'),
    )


class PositionGreeks(Base):
    """Position Greeks - stores calculated Greeks for options positions"""
    __tablename__ = "position_greeks"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    position_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("positions.id"), nullable=False, unique=True)
    calculation_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Greeks values
    delta: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 6), nullable=True)
    gamma: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 6), nullable=True)
    theta: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    vega: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    rho: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 4), nullable=True)
    
    # Position-adjusted values
    delta_dollars: Mapped[Optional[Decimal]] = mapped_column(Numeric(16, 2), nullable=True)
    gamma_dollars: Mapped[Optional[Decimal]] = mapped_column(Numeric(16, 2), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    position: Mapped["Position"] = relationship("Position", back_populates="greeks")
    
    __table_args__ = (
        Index('ix_position_greeks_position_id', 'position_id'),
        Index('ix_position_greeks_calculation_date', 'calculation_date'),
    )


class FactorDefinition(Base):
    """Factor definitions - defines available risk factors"""
    __tablename__ = "factor_definitions"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    factor_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'style', 'sector', 'macro'
    calculation_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exposures: Mapped[list["FactorExposure"]] = relationship("FactorExposure", back_populates="factor")


class FactorExposure(Base):
    """Factor exposures - stores portfolio factor exposures"""
    __tablename__ = "factor_exposures"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    portfolio_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False)
    factor_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("factor_definitions.id"), nullable=False)
    calculation_date: Mapped[date] = mapped_column(Date, nullable=False)
    exposure_value: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    exposure_dollar: Mapped[Optional[Decimal]] = mapped_column(Numeric(16, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="factor_exposures")
    factor: Mapped["FactorDefinition"] = relationship("FactorDefinition", back_populates="exposures")
    
    __table_args__ = (
        UniqueConstraint('portfolio_id', 'factor_id', 'calculation_date', 
                        name='uq_factor_exposures_portfolio_factor_date'),
        Index('ix_factor_exposures_portfolio_id_factor_id', 'portfolio_id', 'factor_id'),
        Index('ix_factor_exposures_calculation_date', 'calculation_date'),
    )

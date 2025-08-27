"""
Alert models for risk notifications and portfolio alerts
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, Dict, Any
import enum
from app.database import Base


class AlertType(enum.Enum):
    """Types of alerts"""
    EXPIRATION_RISK = "expiration_risk"
    CONCENTRATION = "concentration" 
    RISK_LIMIT = "risk_limit"
    POSITION_CHANGE = "position_change"
    MARKET_MOVE = "market_move"
    CORRELATION = "correlation"


class AlertPriority(enum.Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(enum.Enum):
    """Alert status"""
    ACTIVE = "active"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"


class Alert(Base):
    """Alert model - stores portfolio risk alerts"""
    __tablename__ = "alerts"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    portfolio_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=True)
    
    type: Mapped[AlertType] = mapped_column(SQLEnum(AlertType), nullable=False)
    priority: Mapped[AlertPriority] = mapped_column(SQLEnum(AlertPriority), nullable=False)
    status: Mapped[AlertStatus] = mapped_column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE)
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # JSON field for positions affected by this alert
    positions_affected: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # JSON field for suggested actions
    actions: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Additional alert metadata
    alert_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    portfolio: Mapped[Optional["Portfolio"]] = relationship("Portfolio")


class AlertRule(Base):
    """Alert rule model - stores user-defined alert conditions"""
    __tablename__ = "alert_rules"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    portfolio_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=True)
    
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    alert_type: Mapped[AlertType] = mapped_column(SQLEnum(AlertType), nullable=False)
    priority: Mapped[AlertPriority] = mapped_column(SQLEnum(AlertPriority), nullable=False)
    
    # Rule conditions stored as JSON
    conditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Whether this rule is currently active
    is_active: Mapped[bool] = mapped_column(default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User")
    portfolio: Mapped[Optional["Portfolio"]] = relationship("Portfolio")
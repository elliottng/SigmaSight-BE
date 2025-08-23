"""
Modeling session models for portfolio what-if analysis
"""
import uuid
from datetime import datetime
from typing import Optional, Any, TYPE_CHECKING

from sqlalchemy import (
    String,
    JSON,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .users import User  # noqa: F401


class ModelingSessionSnapshot(Base):
    """
    Stores temporary portfolio states during what-if analysis.
    Used by the ProForma Analytics feature to model trade impacts.
    """
    __tablename__ = "modeling_session_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    session_id: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default='active'
    )

    # JSONB fields for flexible schema
    base_portfolio_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSON, 
        nullable=False,
        comment="Original portfolio state before modifications"
    )
    modified_portfolio_snapshot: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        comment="Portfolio state after applying changes"
    )
    changes: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        comment="Array of position changes (add/remove/modify)"
    )
    impact_summary: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        comment="Summary of impacts on risk, exposure, P&L"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="modeling_sessions")

    __table_args__ = (
        CheckConstraint(
            status.in_(['active', 'completed', 'cancelled']), 
            name='modeling_session_status_check'
        ),
        Index('idx_active_sessions', 'user_id', 'status'),
    )

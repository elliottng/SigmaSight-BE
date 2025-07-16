"""
History tracking models for exports and data backfill progress
"""
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    CheckConstraint,
    Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from .users import User  # noqa: F401
    from .portfolio import Portfolio  # noqa: F401


class ExportHistory(Base):
    """
    Minimal audit trail for export operations.
    Tracks what was exported, when, and in what format.
    """
    __tablename__ = "export_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    export_type: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="Type of export: portfolio, trades, modeling_session"
    )
    export_format: Mapped[str] = mapped_column(
        String(10), 
        nullable=False,
        comment="Format: csv, json, fix"
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship()

    __table_args__ = (
        CheckConstraint(
            export_type.in_(['portfolio', 'trades', 'modeling_session']), 
            name='export_type_check'
        ),
        CheckConstraint(
            export_format.in_(['csv', 'json', 'fix']), 
            name='export_format_check'
        ),
    )


class HistoricalBackfillProgress(Base):
    """
    Tracks progress of 90-day historical data fetching from Polygon.io.
    One record per portfolio to monitor backfill status.
    """
    __tablename__ = "historical_backfill_progress"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default='pending',
        comment="Status: pending, processing, completed, failed"
    )
    total_symbols: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="Total number of unique symbols to fetch"
    )
    processed_symbols: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="Number of symbols successfully processed"
    )
    failed_symbols: Mapped[int] = mapped_column(
        Integer, 
        nullable=False, 
        default=0,
        comment="Number of symbols that failed to fetch"
    )
    last_error: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Last error message if any"
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
        DateTime(timezone=True),
        comment="When backfill completed (success or failure)"
    )

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship()

    __table_args__ = (
        CheckConstraint(
            status.in_(['pending', 'processing', 'completed', 'failed']), 
            name='backfill_status_check'
        ),
    )

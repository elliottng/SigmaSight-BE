"""
Portfolio Report models
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any
from app.database import Base


class PortfolioReport(Base):
    """Portfolio report model - stores generated portfolio reports"""
    __tablename__ = "portfolio_reports"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    portfolio_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, default="comprehensive")  # comprehensive, risk, performance, etc.
    version: Mapped[str] = mapped_column(String(10), nullable=False, default="2.0")
    
    # Report metadata
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    anchor_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)  # Date the report data is as of
    calculation_engines_status: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=True)  # Status of each engine
    
    # Report content in different formats
    content_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)  # Structured JSON data
    content_markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Markdown format
    content_csv: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # CSV format
    
    # Report metadata
    portfolio_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    position_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_value: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Store as string to preserve precision
    
    # Status and flags
    is_current: Mapped[bool] = mapped_column(default=True)  # Mark the latest report as current
    generation_duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Store generation errors
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="reports")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_portfolio_reports_portfolio_current', 'portfolio_id', 'is_current'),
        Index('idx_portfolio_reports_generated_at', 'generated_at'),
        Index('idx_portfolio_reports_anchor_date', 'anchor_date'),
    )


class ReportGenerationJob(Base):
    """Track report generation jobs for async processing"""
    __tablename__ = "report_generation_jobs"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    portfolio_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False)
    report_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("portfolio_reports.id"), nullable=True)
    
    # Job details
    job_type: Mapped[str] = mapped_column(String(50), nullable=False, default="comprehensive")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending, running, completed, failed
    
    # Progress tracking
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    current_step: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    total_steps: Mapped[int] = mapped_column(Integer, default=8)  # 8 calculation engines
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    estimated_completion_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    portfolio: Mapped["Portfolio"] = relationship("Portfolio")
    report: Mapped[Optional["PortfolioReport"]] = relationship("PortfolioReport")
    
    # Indexes
    __table_args__ = (
        Index('idx_report_jobs_portfolio_status', 'portfolio_id', 'status'),
        Index('idx_report_jobs_status', 'status'),
        Index('idx_report_jobs_created_at', 'created_at'),
    )
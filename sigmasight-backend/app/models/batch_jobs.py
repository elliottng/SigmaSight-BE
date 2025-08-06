"""
Batch job tracking models for audit trail and monitoring
"""
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, String, DateTime, Float, JSON, Enum as SQLEnum, Text, Index
)
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base


class JobStatus(str, Enum):
    """Batch job status enumeration."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"


class BatchJob(Base):
    """
    Track batch job executions for monitoring and audit trail.
    Implements the batch job tracking requirements from Section 1.6.
    """
    __tablename__ = "batch_jobs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Job identification
    job_name = Column(String(100), nullable=False)
    job_type = Column(String(50))  # e.g., 'market_data', 'greeks', 'aggregation'
    portfolio_id = Column(UUID(as_uuid=True), nullable=True)  # If job is portfolio-specific
    
    # Status tracking
    status = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.QUEUED)
    
    # Timing
    scheduled_at = Column(DateTime, nullable=True)  # When job was scheduled to run
    started_at = Column(DateTime, nullable=True)  # When job actually started
    completed_at = Column(DateTime, nullable=True)  # When job completed
    execution_time = Column(Float, nullable=True)  # Duration in seconds
    
    # Job details
    parameters = Column(JSON, nullable=True)  # Input parameters
    result = Column(JSON, nullable=True)  # Job results/output
    error_message = Column(Text, nullable=True)  # Error details if failed
    warnings = Column(JSON, nullable=True)  # List of warnings if any
    
    # Statistics
    records_processed = Column(Float, nullable=True)  # Number of records processed
    records_failed = Column(Float, nullable=True)  # Number of failed records
    
    # Audit
    triggered_by = Column(String(50))  # 'scheduler', 'manual', 'api'
    created_by = Column(String(100), default='batch_scheduler')
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_batch_jobs_status', 'status'),
        Index('idx_batch_jobs_job_name', 'job_name'),
        Index('idx_batch_jobs_portfolio_id', 'portfolio_id'),
        Index('idx_batch_jobs_started_at', 'started_at'),
        Index('idx_batch_jobs_status_started', 'status', 'started_at'),
    )
    
    def __repr__(self):
        return (
            f"<BatchJob(id={self.id}, job_name={self.job_name}, "
            f"status={self.status}, portfolio_id={self.portfolio_id})>"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            'id': str(self.id),
            'job_name': self.job_name,
            'job_type': self.job_type,
            'portfolio_id': str(self.portfolio_id) if self.portfolio_id else None,
            'status': self.status,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'execution_time': self.execution_time,
            'parameters': self.parameters,
            'result': self.result,
            'error_message': self.error_message,
            'warnings': self.warnings,
            'records_processed': self.records_processed,
            'records_failed': self.records_failed,
            'triggered_by': self.triggered_by,
            'created_by': self.created_by
        }


class BatchJobSchedule(Base):
    """
    Store batch job schedules for reference and modification.
    """
    __tablename__ = "batch_job_schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Schedule identification
    schedule_name = Column(String(100), unique=True, nullable=False)
    job_name = Column(String(100), nullable=False)
    
    # Schedule configuration
    cron_expression = Column(String(100))  # Standard cron expression
    timezone = Column(String(50), default='US/Eastern')
    enabled = Column(String(1), default='Y')  # Y/N flag
    
    # Parameters
    default_parameters = Column(JSON, nullable=True)
    
    # Metadata
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return (
            f"<BatchJobSchedule(schedule_name={self.schedule_name}, "
            f"job_name={self.job_name}, cron={self.cron_expression})>"
        )
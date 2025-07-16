"""
Schemas for export history and backfill progress
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import Field

from .base import BaseSchema, TimestampedSchema


class ExportHistoryCreate(BaseSchema):
    """Request schema for recording an export"""
    export_type: str = Field(..., pattern="^(portfolio|trades|modeling_session)$")
    export_format: str = Field(..., pattern="^(csv|json|fix)$")
    file_name: str = Field(..., min_length=1, max_length=255)
    file_size_bytes: Optional[int] = Field(None, ge=0)


class ExportHistoryInDB(BaseSchema):
    """Database representation of export history"""
    id: UUID
    user_id: Optional[UUID] = None
    export_type: str
    export_format: str
    file_name: str
    file_size_bytes: Optional[int] = None
    created_at: datetime


class ExportHistoryResponse(ExportHistoryInDB):
    """API response for export history"""
    pass


class BackfillProgressCreate(BaseSchema):
    """Request schema for creating backfill progress record"""
    portfolio_id: UUID
    total_symbols: int = Field(..., ge=0)


class BackfillProgressUpdate(BaseSchema):
    """Request schema for updating backfill progress"""
    status: Optional[str] = Field(None, pattern="^(pending|processing|completed|failed)$")
    processed_symbols: Optional[int] = Field(None, ge=0)
    failed_symbols: Optional[int] = Field(None, ge=0)
    last_error: Optional[str] = None


class BackfillProgressInDB(TimestampedSchema):
    """Database representation of backfill progress"""
    id: UUID
    portfolio_id: UUID
    status: str
    total_symbols: int
    processed_symbols: int
    failed_symbols: int
    last_error: Optional[str] = None
    completed_at: Optional[datetime] = None


class BackfillProgressResponse(BackfillProgressInDB):
    """API response for backfill progress"""
    progress_percentage: float = Field(
        ..., 
        description="Percentage of symbols processed (0-100)"
    )
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_symbols == 0:
            return 100.0
        return round((self.processed_symbols / self.total_symbols) * 100, 2)

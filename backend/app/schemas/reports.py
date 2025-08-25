"""
Portfolio Report schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from uuid import UUID


class PortfolioReportBase(BaseModel):
    """Base portfolio report schema"""
    portfolio_id: UUID
    report_type: str = "comprehensive"
    version: str = "2.0"
    anchor_date: datetime
    portfolio_name: Optional[str] = None
    position_count: Optional[int] = None
    total_value: Optional[str] = None


class PortfolioReportCreate(PortfolioReportBase):
    """Schema for creating a portfolio report"""
    calculation_engines_status: Optional[Dict[str, Any]] = None
    content_json: Optional[Dict[str, Any]] = None
    content_markdown: Optional[str] = None
    content_csv: Optional[str] = None
    generation_duration_seconds: Optional[int] = None
    error_message: Optional[str] = None


class PortfolioReportUpdate(BaseModel):
    """Schema for updating a portfolio report"""
    content_json: Optional[Dict[str, Any]] = None
    content_markdown: Optional[str] = None
    content_csv: Optional[str] = None
    is_current: Optional[bool] = None
    error_message: Optional[str] = None


class PortfolioReport(PortfolioReportBase):
    """Complete portfolio report schema"""
    id: UUID
    generated_at: datetime
    calculation_engines_status: Optional[Dict[str, Any]] = None
    content_json: Optional[Dict[str, Any]] = None
    content_markdown: Optional[str] = None
    content_csv: Optional[str] = None
    is_current: bool
    generation_duration_seconds: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PortfolioReportSummary(BaseModel):
    """Summary schema for listing reports"""
    id: UUID
    portfolio_id: UUID
    portfolio_name: Optional[str] = None
    report_type: str
    version: str
    generated_at: datetime
    anchor_date: datetime
    position_count: Optional[int] = None
    total_value: Optional[str] = None
    is_current: bool
    formats_available: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class ReportGenerationJobBase(BaseModel):
    """Base report generation job schema"""
    portfolio_id: UUID
    job_type: str = "comprehensive"


class ReportGenerationJobCreate(ReportGenerationJobBase):
    """Schema for creating a report generation job"""
    pass


class ReportGenerationJobUpdate(BaseModel):
    """Schema for updating a report generation job"""
    status: Optional[str] = None
    progress_percentage: Optional[int] = None
    current_step: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    report_id: Optional[UUID] = None


class ReportGenerationJob(ReportGenerationJobBase):
    """Complete report generation job schema"""
    id: UUID
    report_id: Optional[UUID] = None
    status: str
    progress_percentage: int
    current_step: Optional[str] = None
    total_steps: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int
    max_retries: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportContentResponse(BaseModel):
    """Response schema for report content"""
    format: str
    content: str
    filename: str
    report_id: UUID
    generated_at: datetime
    
    
class AvailableFormatsResponse(BaseModel):
    """Response schema for available report formats"""
    report_id: UUID
    formats: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)
"""
Schemas for factor definitions and exposures
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import Field

from .base import BaseSchema, TimestampedSchema


class FactorDefinitionCreate(BaseSchema):
    """Request schema for creating a factor definition"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    factor_type: str = Field(..., pattern="^(style|sector|macro)$")
    calculation_method: Optional[str] = Field(None, max_length=50)
    etf_proxy: Optional[str] = Field(None, max_length=10)
    display_order: int = Field(..., ge=0)
    is_active: bool = True


class FactorDefinitionUpdate(BaseSchema):
    """Request schema for updating a factor definition"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    factor_type: Optional[str] = Field(None, pattern="^(style|sector|macro)$")
    calculation_method: Optional[str] = Field(None, max_length=50)
    etf_proxy: Optional[str] = Field(None, max_length=10)
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class FactorDefinitionInDB(TimestampedSchema):
    """Database representation of a factor definition"""
    id: UUID
    name: str
    description: Optional[str] = None
    factor_type: str
    calculation_method: Optional[str] = None
    etf_proxy: Optional[str] = None
    display_order: int
    is_active: bool


class FactorDefinitionResponse(FactorDefinitionInDB):
    """API response for factor definition"""
    pass


class FactorExposureCreate(BaseSchema):
    """Request schema for creating factor exposure"""
    position_id: UUID
    factor_id: UUID
    exposure_value: float = Field(..., ge=-10.0, le=10.0)
    calculation_date: datetime


class FactorExposureInDB(TimestampedSchema):
    """Database representation of factor exposure"""
    id: UUID
    position_id: UUID
    factor_id: UUID
    exposure_value: float
    calculation_date: datetime


class FactorExposureResponse(BaseSchema):
    """API response for factor exposure with factor details"""
    factor_name: str
    factor_type: str
    exposure_value: float
    calculation_date: datetime

"""
Pydantic schemas for correlation analysis
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator


# Position filtering schemas
class PositionFilterConfig(BaseModel):
    """Configuration for position filtering in correlation calculations"""
    min_position_value: Optional[Decimal] = Field(default=Decimal("10000"), description="Minimum absolute position value")
    min_portfolio_weight: Optional[Decimal] = Field(default=Decimal("0.01"), description="Minimum portfolio weight")
    filter_mode: str = Field(default="both", pattern="^(value_only|weight_only|both|either)$")
    correlation_threshold: Decimal = Field(default=Decimal("0.7"), ge=0, le=1)
    
    model_config = ConfigDict(from_attributes=True)


# Correlation calculation schemas
class CorrelationCalculationBase(BaseModel):
    """Base schema for correlation calculations"""
    portfolio_id: UUID
    duration_days: int = Field(default=90)
    calculation_date: datetime
    min_position_value: Optional[Decimal] = None
    min_portfolio_weight: Optional[Decimal] = None
    filter_mode: str = Field(default="both")
    correlation_threshold: Decimal = Field(default=Decimal("0.7"))


class CorrelationCalculationCreate(CorrelationCalculationBase):
    """Schema for creating a correlation calculation"""
    force_recalculate: bool = Field(default=False)


class CorrelationCalculationUpdate(BaseModel):
    """Schema for updating correlation calculation metadata"""
    data_quality: Optional[str] = None
    positions_included: Optional[int] = None
    positions_excluded: Optional[int] = None


class CorrelationCalculationResponse(CorrelationCalculationBase):
    """Response schema for correlation calculation"""
    id: UUID
    overall_correlation: Decimal
    correlation_concentration_score: Decimal
    effective_positions: Decimal
    data_quality: str
    positions_included: int
    positions_excluded: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Cluster schemas
class ClusterPositionResponse(BaseModel):
    """Response schema for positions within a cluster"""
    position_id: UUID
    symbol: str
    value: Decimal
    portfolio_percentage: Decimal
    correlation_to_cluster: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class CorrelationClusterResponse(BaseModel):
    """Response schema for correlation clusters"""
    id: UUID
    cluster_number: int
    nickname: str
    avg_correlation: Decimal
    total_value: Decimal
    portfolio_percentage: Decimal
    positions: List[ClusterPositionResponse]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Pairwise correlation schemas
class PairwiseCorrelationCreate(BaseModel):
    """Schema for creating pairwise correlations"""
    correlation_calculation_id: UUID
    symbol_1: str
    symbol_2: str
    correlation_value: Decimal
    data_points: int
    statistical_significance: Optional[Decimal] = None


class PairwiseCorrelationResponse(BaseModel):
    """Response schema for pairwise correlations"""
    id: UUID
    symbol_1: str
    symbol_2: str
    correlation_value: Decimal
    data_points: int
    statistical_significance: Optional[Decimal] = None
    
    model_config = ConfigDict(from_attributes=True)


# Matrix response schemas
class CorrelationMatrixResponse(BaseModel):
    """Response schema for correlation matrix endpoint"""
    correlation_matrix: Dict[str, List[float]]  # {"symbols": ["A", "B"], "correlations": [[1.0, 0.8], [0.8, 1.0]]}
    position_metadata: List[Dict[str, Any]]
    calculation_date: datetime
    duration_days: int
    position_filters: Dict[str, Any]
    filters_applied: Dict[str, Any]
    
    model_config = ConfigDict(from_attributes=True)


# Portfolio correlation metrics response
class PortfolioCorrelationMetricsResponse(BaseModel):
    """Response schema for portfolio-level correlation metrics"""
    overall_correlation: Decimal
    correlation_concentration_score: Decimal
    effective_positions: Decimal
    clusters: List[CorrelationClusterResponse]
    calculation_date: datetime
    duration_days: int
    position_filters: Dict[str, Any]
    data_quality: str
    
    model_config = ConfigDict(from_attributes=True)


# Request schemas for API endpoints
class CalculateCorrelationRequest(BaseModel):
    """Request schema for triggering correlation calculation"""
    portfolio_id: UUID
    duration_days: int = Field(default=90)
    position_filters: PositionFilterConfig = Field(default_factory=PositionFilterConfig)
    force_recalculate: bool = Field(default=False)


class CorrelationMatrixRequest(BaseModel):
    """Request schema for correlation matrix query"""
    min_position_value: Optional[Decimal] = None
    min_portfolio_weight: Optional[Decimal] = None
    filter_mode: str = Field(default="both")
    min_correlation: Optional[Decimal] = Field(None, ge=-1, le=1)
    max_correlation: Optional[Decimal] = Field(None, ge=-1, le=1)
    position_types: Optional[List[str]] = None
    min_dollar_exposure: Optional[Decimal] = None
    min_delta_exposure: Optional[Decimal] = None
    view: str = Field(default="portfolio", pattern="^(portfolio|longs|shorts)$")
    
    @field_validator('min_correlation', 'max_correlation')
    def validate_correlation_range(cls, v, values):
        if 'min_correlation' in values and 'max_correlation' in values:
            if values['min_correlation'] and values['max_correlation']:
                if values['min_correlation'] > values['max_correlation']:
                    raise ValueError('min_correlation must be less than or equal to max_correlation')
        return v
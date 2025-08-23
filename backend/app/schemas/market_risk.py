"""
Pydantic schemas for Market Risk Scenarios - Section 1.4.5
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class MarketRiskScenarioBase(BaseModel):
    """Base schema for market risk scenarios"""
    portfolio_id: UUID
    scenario_type: str = Field(..., description="Scenario type (e.g., 'market_up_5', 'ir_down_100bp')")
    scenario_value: Decimal = Field(..., description="Scenario change value (e.g., 0.05 for +5%)")
    predicted_pnl: Decimal = Field(..., description="Predicted P&L for this scenario")
    calculation_date: date


class MarketRiskScenarioCreate(MarketRiskScenarioBase):
    """Schema for creating market risk scenarios"""
    pass


class MarketRiskScenarioResponse(MarketRiskScenarioBase):
    """Schema for market risk scenario responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime


class MarketRiskScenarioUpdate(BaseModel):
    """Schema for updating market risk scenarios"""
    scenario_value: Optional[Decimal] = None
    predicted_pnl: Optional[Decimal] = None


class PositionInterestRateBetaBase(BaseModel):
    """Base schema for position interest rate betas"""
    position_id: UUID
    ir_beta: Decimal = Field(..., description="Interest rate beta coefficient")
    r_squared: Optional[Decimal] = Field(None, description="Regression R-squared value")
    calculation_date: date


class PositionInterestRateBetaCreate(PositionInterestRateBetaBase):
    """Schema for creating position interest rate betas"""
    pass


class PositionInterestRateBetaResponse(PositionInterestRateBetaBase):
    """Schema for position interest rate beta responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime


class PositionInterestRateBetaUpdate(BaseModel):
    """Schema for updating position interest rate betas"""
    ir_beta: Optional[Decimal] = None
    r_squared: Optional[Decimal] = None


# Market scenario calculation request/response schemas

class MarketScenarioRequest(BaseModel):
    """Request schema for market scenario calculations"""
    portfolio_id: UUID
    calculation_date: Optional[date] = Field(default=None, description="Date for calculation (defaults to today)")
    custom_scenarios: Optional[Dict[str, float]] = Field(
        default=None,
        description="Custom market scenarios (e.g., {'custom_up_15': 0.15})"
    )


class InterestRateScenarioRequest(BaseModel):
    """Request schema for interest rate scenario calculations"""
    portfolio_id: UUID
    calculation_date: Optional[date] = Field(default=None, description="Date for calculation (defaults to today)")
    treasury_series: Optional[str] = Field(default="10Y", description="Treasury series to use (3M, 2Y, 10Y, 30Y)")
    custom_scenarios: Optional[Dict[str, float]] = Field(
        default=None,
        description="Custom IR scenarios (e.g., {'custom_up_300bp': 0.03})"
    )


class ScenarioResult(BaseModel):
    """Individual scenario result"""
    scenario_value: float = Field(..., description="Scenario change value")
    predicted_pnl: float = Field(..., description="Predicted P&L")
    additional_info: Optional[Dict[str, Any]] = Field(default=None, description="Additional scenario information")


class MarketScenarioResponse(BaseModel):
    """Response schema for market scenario calculations"""
    portfolio_id: UUID
    calculation_date: date
    market_beta: float = Field(..., description="Portfolio market beta")
    portfolio_value: float = Field(..., description="Total portfolio value")
    scenarios: Dict[str, ScenarioResult] = Field(..., description="Scenario results")
    records_stored: int = Field(..., description="Number of records stored in database")
    data_quality: Dict[str, Any] = Field(..., description="Data quality information")


class InterestRateScenarioResponse(BaseModel):
    """Response schema for interest rate scenario calculations"""
    portfolio_id: UUID
    calculation_date: date
    portfolio_ir_beta: float = Field(..., description="Portfolio-weighted interest rate beta")
    portfolio_value: float = Field(..., description="Total portfolio value")
    treasury_series: str = Field(..., description="Treasury series used")
    scenarios: Dict[str, ScenarioResult] = Field(..., description="Interest rate scenario results")
    records_stored: int = Field(..., description="Number of records stored in database")
    position_count: int = Field(..., description="Number of positions analyzed")


class MarketBetaResponse(BaseModel):
    """Response schema for portfolio market beta calculation"""
    portfolio_id: UUID
    calculation_date: date
    market_beta: float = Field(..., description="Portfolio market beta")
    portfolio_value: float = Field(..., description="Total portfolio value")
    factor_breakdown: Dict[str, float] = Field(..., description="Factor beta breakdown")
    data_quality: Dict[str, Any] = Field(..., description="Data quality metrics")
    positions_count: int = Field(..., description="Number of positions in portfolio")


class PositionInterestRateBetasResponse(BaseModel):
    """Response schema for position interest rate betas calculation"""
    portfolio_id: UUID
    calculation_date: date
    treasury_series: str = Field(..., description="Treasury series used")
    position_ir_betas: Dict[str, Dict[str, float]] = Field(..., description="Position-level IR betas")
    records_stored: int = Field(..., description="Number of records stored")
    regression_days: int = Field(..., description="Number of days used in regression")
    treasury_data_points: int = Field(..., description="Number of Treasury data points")


# List response schemas

class MarketRiskScenarioList(BaseModel):
    """List response for market risk scenarios"""
    scenarios: List[MarketRiskScenarioResponse]
    total_count: int
    portfolio_id: Optional[UUID] = None
    date_range: Optional[Dict[str, date]] = None


class PositionInterestRateBetaList(BaseModel):
    """List response for position interest rate betas"""
    betas: List[PositionInterestRateBetaResponse]
    total_count: int
    portfolio_id: Optional[UUID] = None
    position_id: Optional[UUID] = None
    date_range: Optional[Dict[str, date]] = None


# Summary schemas for reporting

class MarketRiskSummary(BaseModel):
    """Summary of market risk scenarios for a portfolio"""
    portfolio_id: UUID
    calculation_date: date
    total_scenarios: int
    worst_case_pnl: float = Field(..., description="Worst case P&L across all scenarios")
    best_case_pnl: float = Field(..., description="Best case P&L across all scenarios")
    market_scenarios_count: int
    interest_rate_scenarios_count: int
    portfolio_value: float


class RiskScenarioAnalysis(BaseModel):
    """Comprehensive risk scenario analysis"""
    portfolio_id: UUID
    analysis_date: date
    market_risk_summary: MarketRiskSummary
    top_market_risks: List[Dict[str, Any]] = Field(..., description="Top market risk scenarios")
    top_ir_risks: List[Dict[str, Any]] = Field(..., description="Top interest rate risk scenarios")
    risk_concentration: Dict[str, float] = Field(..., description="Risk concentration by scenario type")
    data_quality_score: float = Field(..., description="Overall data quality score (0-1)")
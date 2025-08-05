"""
Pydantic schemas for Comprehensive Stress Testing Framework - Section 1.4.7
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class StressTestScenarioBase(BaseModel):
    """Base schema for stress test scenarios"""
    scenario_id: str = Field(..., description="Unique scenario identifier")
    name: str = Field(..., description="Human-readable scenario name")
    description: Optional[str] = Field(None, description="Detailed scenario description")
    category: str = Field(..., description="Scenario category (market, rates, rotation, volatility, historical)")
    severity: str = Field(..., description="Severity level (mild, moderate, severe, extreme)")
    shock_config: Dict[str, Any] = Field(..., description="Configuration for shocked factors")
    active: bool = Field(default=True, description="Whether scenario is active")


class StressTestScenarioCreate(StressTestScenarioBase):
    """Schema for creating stress test scenarios"""
    pass


class StressTestScenarioResponse(StressTestScenarioBase):
    """Schema for stress test scenario responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: datetime


class StressTestScenarioUpdate(BaseModel):
    """Schema for updating stress test scenarios"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    shock_config: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None


class StressTestResultBase(BaseModel):
    """Base schema for stress test results"""
    portfolio_id: UUID
    scenario_id: UUID
    calculation_date: date
    direct_pnl: Decimal = Field(..., description="Direct impact P&L without correlations")
    correlated_pnl: Decimal = Field(..., description="Correlated impact P&L with factor correlations")
    correlation_effect: Decimal = Field(..., description="Difference between correlated and direct P&L")
    factor_impacts: Optional[Dict[str, Any]] = Field(None, description="Detailed factor-level impacts")
    calculation_metadata: Optional[Dict[str, Any]] = Field(None, description="Calculation details and metadata")


class StressTestResultCreate(StressTestResultBase):
    """Schema for creating stress test results"""
    pass


class StressTestResultResponse(StressTestResultBase):
    """Schema for stress test result responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime


class FactorCorrelationBase(BaseModel):
    """Base schema for factor correlations"""
    factor_1_id: UUID
    factor_2_id: UUID
    correlation: Decimal = Field(..., description="Correlation coefficient (-1 to 1)")
    calculation_date: date
    lookback_days: int = Field(..., description="Historical period used for calculation")
    decay_factor: Decimal = Field(..., description="Exponential decay factor")
    data_points: int = Field(..., description="Number of data points used")


class FactorCorrelationCreate(FactorCorrelationBase):
    """Schema for creating factor correlations"""
    pass


class FactorCorrelationResponse(FactorCorrelationBase):
    """Schema for factor correlation responses"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime


# Request/Response schemas for stress testing operations

class FactorCorrelationMatrixRequest(BaseModel):
    """Request schema for factor correlation matrix calculation"""
    lookback_days: Optional[int] = Field(default=252, description="Historical period for correlation (default: 252 days)")
    decay_factor: Optional[float] = Field(default=0.94, description="Exponential decay factor (default: 0.94)")


class FactorCorrelationMatrixResponse(BaseModel):
    """Response schema for factor correlation matrix calculation"""
    correlation_matrix: Dict[str, Dict[str, float]] = Field(..., description="Factor-to-factor correlation matrix")
    factor_names: List[str] = Field(..., description="List of factor names")
    calculation_date: date
    lookback_days: int
    decay_factor: float
    data_days: int = Field(..., description="Number of trading days used")
    matrix_stats: Dict[str, float] = Field(..., description="Matrix statistics (mean, max, min, std)")


class DirectStressImpactRequest(BaseModel):
    """Request schema for direct stress impact calculation"""
    portfolio_id: UUID
    scenario_config: Dict[str, Any] = Field(..., description="Scenario configuration with shocked factors")
    calculation_date: Optional[date] = Field(default=None, description="Date for calculation (defaults to today)")


class DirectStressImpactResponse(BaseModel):
    """Response schema for direct stress impact calculation"""
    scenario_name: str
    scenario_id: Optional[str] = None
    portfolio_id: UUID
    calculation_date: date
    shocked_factors: Dict[str, float] = Field(..., description="Factors and their shock amounts")
    factor_impacts: Dict[str, Dict[str, float]] = Field(..., description="Factor-level impact breakdown")
    total_direct_pnl: float = Field(..., description="Total direct P&L impact")
    calculation_method: str = Field(default="direct")
    factor_exposures_date: date = Field(..., description="Date of factor exposures used")


class CorrelatedStressImpactRequest(BaseModel):
    """Request schema for correlated stress impact calculation"""
    portfolio_id: UUID
    scenario_config: Dict[str, Any] = Field(..., description="Scenario configuration with shocked factors")
    correlation_matrix: Dict[str, Dict[str, float]] = Field(..., description="Factor correlation matrix")
    calculation_date: Optional[date] = Field(default=None, description="Date for calculation (defaults to today)")


class CorrelatedStressImpactResponse(BaseModel):
    """Response schema for correlated stress impact calculation"""
    scenario_name: str
    scenario_id: Optional[str] = None
    portfolio_id: UUID
    calculation_date: date
    shocked_factors: Dict[str, float]
    direct_pnl: float = Field(..., description="Direct P&L without correlations")
    correlated_pnl: float = Field(..., description="Correlated P&L with factor correlations")
    correlation_effect: float = Field(..., description="Additional P&L from correlations")
    factor_impacts: Dict[str, Dict[str, Any]] = Field(..., description="Factor-level correlated impacts")
    calculation_method: str = Field(default="correlated")
    correlation_matrix_stats: Dict[str, Any] = Field(..., description="Correlation matrix metadata")


class ComprehensiveStressTestRequest(BaseModel):
    """Request schema for comprehensive stress test"""
    portfolio_id: UUID
    calculation_date: Optional[date] = Field(default=None, description="Date for calculation (defaults to today)")
    scenario_filter: Optional[List[str]] = Field(default=None, description="Categories to include (defaults to all)")
    config_path: Optional[str] = Field(default=None, description="Path to custom scenario configuration")


class StressTestSummaryStats(BaseModel):
    """Summary statistics for stress test results"""
    worst_case_pnl: float = Field(..., description="Worst case P&L across all scenarios")
    best_case_pnl: float = Field(..., description="Best case P&L across all scenarios")
    mean_pnl: float = Field(..., description="Mean P&L across scenarios")
    median_pnl: float = Field(..., description="Median P&L across scenarios")
    pnl_std: float = Field(..., description="Standard deviation of P&L")
    mean_correlation_effect: float = Field(..., description="Mean correlation effect across scenarios")
    scenarios_negative: int = Field(..., description="Number of scenarios with negative P&L")
    scenarios_positive: int = Field(..., description="Number of scenarios with positive P&L")


class ComprehensiveStressTestResponse(BaseModel):
    """Response schema for comprehensive stress test"""
    portfolio_id: UUID
    portfolio_name: str
    calculation_date: date
    correlation_matrix_info: Dict[str, Any] = Field(..., description="Correlation matrix metadata")
    stress_test_results: Dict[str, Any] = Field(..., description="Complete stress test results by category")
    summary_stats: StressTestSummaryStats = Field(..., description="Summary statistics")
    config_metadata: Dict[str, Any] = Field(..., description="Configuration metadata")


class StressScenarioResult(BaseModel):
    """Individual stress scenario result"""
    scenario_id: str
    scenario_name: str
    category: str
    severity: str
    direct_pnl: float
    correlated_pnl: float
    correlation_effect: float
    shocked_factors: Dict[str, float]


class StressTestReport(BaseModel):
    """Comprehensive stress test report"""
    portfolio_id: UUID
    portfolio_name: str
    report_date: date
    summary_stats: StressTestSummaryStats
    top_risks: List[StressScenarioResult] = Field(..., description="Top risk scenarios by absolute P&L")
    top_opportunities: List[StressScenarioResult] = Field(..., description="Top opportunity scenarios by positive P&L")
    category_breakdown: Dict[str, Dict[str, float]] = Field(..., description="Risk breakdown by category")
    correlation_insights: Dict[str, Any] = Field(..., description="Key correlation insights")
    risk_concentration: Dict[str, float] = Field(..., description="Risk concentration by factor")


# List response schemas

class StressTestScenarioList(BaseModel):
    """List response for stress test scenarios"""
    scenarios: List[StressTestScenarioResponse]
    total_count: int
    category_filter: Optional[str] = None
    active_only: bool = False


class StressTestResultList(BaseModel):
    """List response for stress test results"""
    results: List[StressTestResultResponse]
    total_count: int
    portfolio_id: Optional[UUID] = None
    date_range: Optional[Dict[str, date]] = None


class FactorCorrelationList(BaseModel):
    """List response for factor correlations"""
    correlations: List[FactorCorrelationResponse]
    total_count: int
    calculation_date: Optional[date] = None


# Configuration schemas

class StressTestConfiguration(BaseModel):
    """Stress test configuration settings"""
    default_lookback_days: int = Field(default=252)
    correlation_decay_factor: float = Field(default=0.94)
    min_factor_correlation: float = Field(default=-0.95)
    max_factor_correlation: float = Field(default=0.95)
    stress_magnitude_cap: float = Field(default=1.0)
    enable_cross_correlations: bool = Field(default=True)
    default_confidence_level: float = Field(default=0.95)


class SeverityLevel(BaseModel):
    """Severity level definition"""
    description: str
    impact_range: str


class StressTestConfigurationResponse(BaseModel):
    """Response schema for stress test configuration"""
    configuration: StressTestConfiguration
    factor_mappings: Dict[str, str] = Field(..., description="Factor name to ETF symbol mappings")
    severity_levels: Dict[str, SeverityLevel] = Field(..., description="Severity level definitions")
    total_scenarios: int = Field(..., description="Total number of available scenarios")
    active_scenarios: int = Field(..., description="Number of active scenarios")
    categories: List[str] = Field(..., description="Available scenario categories")
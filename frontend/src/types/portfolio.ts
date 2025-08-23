export interface Portfolio {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  user_id: string;
}

export interface PortfolioSnapshot {
  date: string;
  total_value: string;
  daily_pnl: string;
  daily_return: string;
}

export interface PositionExposures {
  gross_exposure: string;
  net_exposure: string;
  long_exposure: string;
  short_exposure: string;
  long_count: number;
  short_count: number;
  options_exposure: string;
  stock_exposure: string;
  notional: string;
  metadata: {
    calculated_at: string;
    position_count: number;
    warnings: string[];
  };
}

export interface GreeksAggregation {
  delta: string;
  gamma: string;
  theta: string;
  vega: string;
  rho: string;
  metadata: {
    calculated_at: string;
    positions_with_greeks: number;
    positions_without_greeks: number;
    warnings: string[];
  };
}

export interface FactorExposure {
  factor_name: string;
  category: string;
  exposure_value: string;
  exposure_dollar: string | null;
  calculation_date: string;
}

export interface PortfolioReport {
  version: string;
  metadata: {
    portfolio_id: string;
    portfolio_name: string;
    report_date: string;
    anchor_date: string;
    generated_at: string;
    precision_policy: {
      monetary_values: string;
      greeks: string;
      correlations: string;
      factor_exposures: string;
    };
  };
  portfolio_info: {
    id: string;
    name: string;
    created_at: string;
    position_count: number;
  };
  calculation_engines: {
    portfolio_snapshot: {
      available: boolean;
      data: PortfolioSnapshot;
      description: string;
    };
    position_exposures: {
      available: boolean;
      data: PositionExposures;
      description: string;
    };
    greeks_aggregation: {
      available: boolean;
      data: GreeksAggregation;
      description: string;
    };
    factor_analysis: {
      available: boolean;
      count: number;
      data: FactorExposure[];
      description: string;
    };
    correlation_analysis: {
      available: boolean;
      data: any;
      description: string;
    };
    market_data: {
      available: boolean;
      position_count: number;
      description: string;
    };
    stress_testing: {
      available: boolean;
      scenario_count: number;
      data: any;
      description: string;
    };
    interest_rate_betas: {
      available: boolean;
      data: any;
      description: string;
    };
  };
  positions_summary: {
    count: number;
    long_count: number;
    short_count: number;
    options_count: number;
    stock_count: number;
  };
}
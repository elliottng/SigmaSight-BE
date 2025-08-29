// Authentication types
export interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

// Portfolio types
export interface Portfolio {
  id: string
  user_id: string
  name: string
  created_at: string
  updated_at: string
}

export interface PortfolioOverview {
  total_value: number
  total_pl: number
  total_pl_percent: number
  exposures: {
    long: ExposureValue
    short: ExposureValue
    gross: ExposureValue
    net: ExposureValue
  }
  exposure_calculations: {
    delta: ExposureCalculation
    notional: ExposureCalculation
  }
  ai_insights?: {
    primary_risks: string[]
    opportunities: string[]
  }
}

export interface ExposureValue {
  value: number
  visual: VisualIndicator
}

export interface ExposureCalculation {
  long_exposure: number
  short_exposure: number
  gross_exposure: number
  net_exposure: number
}

export interface VisualIndicator {
  percentage?: number
  status?: 'success' | 'warning' | 'danger' | 'info'
  color?: string
  target_range?: [number, number]
  limit?: number
  display?: string
}

// Position types
export type PositionType = 'LONG' | 'SHORT' | 'LC' | 'LP' | 'SC' | 'SP'

export interface Position {
  id: string
  ticker: string
  name: string
  type: PositionType
  quantity: number
  price: number
  value: number
  pnl: number
  pnl_percent: number
  tags: string[]
  notional_exposure: number
  risk_metrics?: {
    beta: number
    risk_contribution: number
  }
  strike?: number
  expiration?: string
  market_value?: number
  exposure?: number
  greeks?: PositionGreeks
}

export interface PositionGreeks {
  delta: number
  gamma: number
  theta: number
  vega: number
  rho?: number
}

export interface PositionsResponse {
  positions: Position[]
  summary: {
    total_positions: number
    gross_exposure: number
    net_exposure: number
  }
}

// Risk types
export interface RiskOverview {
  view: 'portfolio' | 'longs' | 'shorts'
  period: 'daily' | 'weekly' | 'monthly' | 'annual'
  metrics: {
    beta: RiskMetric
    annualized_volatility: RiskMetric
    position_correlation: RiskMetric
    max_drawdown: RiskMetric
    var_1d: RiskMetric & { confidence: number }
  }
  ai_risk_summary?: {
    biggest_risks: Array<{
      type: string
      description: string
      severity: 'low' | 'medium' | 'high' | 'critical'
      suggested_actions: string[]
    }>
  }
}

export interface RiskMetric {
  value: number | string
  description: string
  visual?: VisualIndicator
}

export interface GreeksResponse {
  current: {
    delta: number
    gamma: number
    theta: number
    vega: number
    visual?: {
      gamma_status: 'success' | 'warning' | 'danger'
      gamma_message: string
    }
  }
  after_expiry?: {
    delta: number
    gamma: number
    changes: {
      delta: number
      gamma: number
      gamma_percent: number
    }
  }
}

// Factor types
export interface FactorDefinition {
  factor_name: string
  etf_ticker: string | null
  description: string
  calculation_method: 'real' | 'mock'
  display_order: number
}

export interface FactorExposure {
  factor_name: string
  exposure: number
  exposure_visual: VisualIndicator
}

// Market data types
export interface MarketQuote {
  symbol: string
  price: number
  change: number
  change_percent: number
  volume?: number
  timestamp?: string
}

// Report types
export interface ReportTemplate {
  id: string
  name: string
  description: string
  sections: string[]
  format: 'pdf' | 'json' | 'csv'
}

// Alert types
export interface Alert {
  id: string
  type: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  title: string
  message: string
  positions_affected?: string[]
  triggered_at: string
  actions?: string[]
}

// Modeling types
export interface ModelingSession {
  session_id: string
  name: string
  status: 'active' | 'closed'
  original_portfolio: PortfolioOverview
  modified_portfolio: PortfolioOverview
  changes: Array<{
    action: 'add' | 'modify' | 'remove'
    position_id: string
    field?: string
    from?: any
    to?: any
  }>
  impact: {
    net_exposure_change: number
    tech_exposure_change?: number
    greeks_change?: Partial<PositionGreeks>
  }
}

// Pagination types
export interface PaginatedResponse<T> {
  data: T[]
  meta: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

// Error types
export interface ApiError {
  code: string
  message: string
  field?: string
  ai_suggestions?: string[]
}
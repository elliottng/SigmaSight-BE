export type PositionType = 'LONG' | 'SHORT' | 'LC' | 'LP' | 'SC' | 'SP';

export interface Position {
  id: string;
  portfolio_id: string;
  symbol: string;
  position_type: PositionType;
  quantity: number;
  entry_price: number;
  entry_date: string;
  exit_date?: string;
  current_price?: number;
  market_value?: number;
  cost_basis?: number;
  unrealized_pnl?: number;
  realized_pnl?: number;
  daily_pnl?: number;
  total_pnl?: number;
  
  // Options fields
  strike_price?: number;
  expiration_date?: string;
  underlying_symbol?: string;
  days_to_expiry?: number;
  
  // Greeks
  delta?: number;
  gamma?: number;
  theta?: number;
  vega?: number;
  rho?: number;
  
  // Additional metadata
  sector?: string;
  industry?: string;
  tags?: string[];
  notes?: string;
  
  // Portfolio context
  portfolio_name?: string;
  portfolio_weight?: number;
  position_exposure?: number;
}

export interface PositionTableRow extends Position {
  gross_exposure: number;
  net_exposure: number;
  notional: number;
}

export interface PositionFilters {
  search: string;
  type: PositionType | 'All';
  tags: string[];
  sortBy: 'symbol' | 'pnl' | 'exposure' | 'type';
  sortOrder: 'asc' | 'desc';
}

export interface GreeksData {
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
}
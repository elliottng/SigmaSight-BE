import { apiClient, handleApiResponse } from '../lib/api'
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
  PortfolioOverview,
  PositionsResponse,
  Position,
  RiskOverview,
  GreeksResponse,
  FactorDefinition,
  FactorExposure,
  MarketQuote,
  Alert,
  ModelingSession,
  ReportTemplate,
} from '../lib/types'

// Authentication API
export const authApi = {
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post('/auth/login', credentials)
    return handleApiResponse(response)
  },

  register: async (userData: RegisterRequest): Promise<User> => {
    const response = await apiClient.post('/auth/register', userData)
    return handleApiResponse(response)
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/auth/me')
    return handleApiResponse(response)
  },

  refreshToken: async (): Promise<TokenResponse> => {
    const response = await apiClient.post('/auth/refresh')
    return handleApiResponse(response)
  },
}

// Portfolio API
export const portfolioApi = {
  getOverview: async (): Promise<PortfolioOverview> => {
    const response = await apiClient.get('/portfolio')
    return handleApiResponse(response)
  },

  getSummary: async (): Promise<any> => {
    const response = await apiClient.get('/portfolio/summary')
    return handleApiResponse(response)
  },

  getTimeline: async (params?: { start?: string; end?: string }): Promise<any> => {
    const response = await apiClient.get('/portfolio/timeline', { params })
    return handleApiResponse(response)
  },

  uploadCsv: async (file: File): Promise<any> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post('/portfolio/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return handleApiResponse(response)
  },
}

// Positions API
export const positionsApi = {
  getPositions: async (params?: {
    groupBy?: string
    tags?: string
    tagMode?: string
    fields?: string
  }): Promise<PositionsResponse> => {
    const response = await apiClient.get('/positions', { params })
    return handleApiResponse(response)
  },

  addPosition: async (position: Partial<Position>): Promise<Position> => {
    const response = await apiClient.post('/positions', position)
    return handleApiResponse(response)
  },

  updatePosition: async (id: string, updates: Partial<Position>): Promise<Position> => {
    const response = await apiClient.put(`/positions/${id}`, updates)
    return handleApiResponse(response)
  },

  deletePosition: async (id: string): Promise<void> => {
    const response = await apiClient.delete(`/positions/${id}`)
    return handleApiResponse(response)
  },

  getGroupedPositions: async (): Promise<any> => {
    const response = await apiClient.get('/positions/grouped')
    return handleApiResponse(response)
  },

  getAttribution: async (params?: {
    date?: string
    groupBy?: string
  }): Promise<any> => {
    const response = await apiClient.get('/attribution/positions', { params })
    return handleApiResponse(response)
  },
}

// Risk API
export const riskApi = {
  getOverview: async (params?: {
    view?: string
    period?: string
  }): Promise<RiskOverview> => {
    const response = await apiClient.get('/risk/overview', { params })
    return handleApiResponse(response)
  },

  getGreeks: async (params?: {
    include_after_expiry?: boolean
    view?: string
  }): Promise<GreeksResponse> => {
    const response = await apiClient.get('/risk/greeks', { params })
    return handleApiResponse(response)
  },

  calculateGreeks: async (positions: Partial<Position>[]): Promise<any> => {
    const response = await apiClient.post('/risk/greeks/calculate', { positions })
    return handleApiResponse(response)
  },

  getFactorDefinitions: async (): Promise<FactorDefinition[]> => {
    const response = await apiClient.get('/risk/factors/definitions')
    return handleApiResponse(response)
  },

  getFactorExposures: async (params?: {
    view?: string
    period?: string
  }): Promise<FactorExposure[]> => {
    const response = await apiClient.get('/risk/factors', { params })
    return handleApiResponse(response)
  },

  getPositionFactorExposures: async (params?: {
    portfolio_id?: string
    position_ids?: string
    factors?: string
  }): Promise<any> => {
    const response = await apiClient.get('/risk/factors/positions', { params })
    return handleApiResponse(response)
  },

  runScenarioAnalysis: async (scenarios: any): Promise<any> => {
    const response = await apiClient.post('/risk/scenarios', scenarios)
    return handleApiResponse(response)
  },

  getScenarioTemplates: async (): Promise<any> => {
    const response = await apiClient.get('/risk/scenarios/templates')
    return handleApiResponse(response)
  },
}

// Market Data API
export const marketDataApi = {
  getQuotes: async (symbols: string[]): Promise<MarketQuote[]> => {
    const response = await apiClient.get('/market/quotes', {
      params: { symbols: symbols.join(',') }
    })
    return handleApiResponse(response)
  },

  getOptionsChain: async (params: {
    symbol: string
    expiry?: string
    strikes?: number
  }): Promise<any> => {
    const response = await apiClient.get('/market/options', { params })
    return handleApiResponse(response)
  },
}

// Alerts API
export const alertsApi = {
  getAlerts: async (params?: { priority?: string }): Promise<Alert[]> => {
    const response = await apiClient.get('/alerts', { params })
    return handleApiResponse(response)
  },

  createAlertRule: async (rule: any): Promise<any> => {
    const response = await apiClient.post('/alerts/rules', rule)
    return handleApiResponse(response)
  },

  dismissAlert: async (alertId: string): Promise<void> => {
    const response = await apiClient.delete(`/alerts/${alertId}`)
    return handleApiResponse(response)
  },
}

// Modeling API
export const modelingApi = {
  createSession: async (data: { name: string; base_portfolio?: string }): Promise<ModelingSession> => {
    const response = await apiClient.post('/modeling/sessions', data)
    return handleApiResponse(response)
  },

  getSession: async (sessionId: string): Promise<ModelingSession> => {
    const response = await apiClient.get(`/modeling/sessions/${sessionId}`)
    return handleApiResponse(response)
  },

  updateSessionPositions: async (sessionId: string, modifications: any[]): Promise<any> => {
    const response = await apiClient.put(`/modeling/sessions/${sessionId}/positions`, {
      modifications
    })
    return handleApiResponse(response)
  },

  resetSession: async (sessionId: string): Promise<void> => {
    const response = await apiClient.post(`/modeling/sessions/${sessionId}/reset`)
    return handleApiResponse(response)
  },

  exportTradeList: async (sessionId: string, format: string = 'csv'): Promise<any> => {
    const response = await apiClient.get(`/modeling/sessions/${sessionId}/export`, {
      params: { format }
    })
    return handleApiResponse(response)
  },

  modelSingleTrade: async (trade: any): Promise<any> => {
    const response = await apiClient.post('/proforma/trade', trade)
    return handleApiResponse(response)
  },

  findOptimalHedges: async (hedgeRequest: any): Promise<any> => {
    const response = await apiClient.post('/proforma/hedge', hedgeRequest)
    return handleApiResponse(response)
  },
}

// Reports API
export const reportsApi = {
  generateReport: async (reportRequest: any): Promise<any> => {
    const response = await apiClient.post('/reports/generate', reportRequest)
    return handleApiResponse(response)
  },

  getReportTemplates: async (): Promise<ReportTemplate[]> => {
    const response = await apiClient.get('/reports/templates')
    return handleApiResponse(response)
  },

  scheduleReport: async (schedule: any): Promise<any> => {
    const response = await apiClient.post('/reports/schedule', schedule)
    return handleApiResponse(response)
  },
}

// Export API
export const exportApi = {
  exportPortfolio: async (params?: {
    format?: string
    include?: string
  }): Promise<any> => {
    const response = await apiClient.get('/export/portfolio', { params })
    return handleApiResponse(response)
  },

  generateTradeList: async (trades: any[]): Promise<any> => {
    const response = await apiClient.post('/export/trades', { trades })
    return handleApiResponse(response)
  },
}

// Job Management API
export const jobsApi = {
  getJobStatus: async (jobId: string): Promise<any> => {
    const response = await apiClient.get(`/jobs/${jobId}`)
    return handleApiResponse(response)
  },

  getJobResult: async (jobId: string): Promise<any> => {
    const response = await apiClient.get(`/jobs/${jobId}/result`)
    return handleApiResponse(response)
  },

  cancelJob: async (jobId: string): Promise<void> => {
    const response = await apiClient.post(`/jobs/${jobId}/cancel`)
    return handleApiResponse(response)
  },
}
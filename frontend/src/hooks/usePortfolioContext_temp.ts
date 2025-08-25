import { useState, useEffect, useCallback } from 'react';
import useSWR from 'swr';

// Portfolio Context Types (aligned with backend API contracts)
export interface PortfolioSummary {
  portfolioId: string;
  asOf: string;
  window: string;
  equity: number;
  cash: number;
  grossExposurePct: number;
  netExposurePct: number;
  longExposurePct: number;
  shortExposurePct: number;
  returnPct: number;
  annVolPct: number;
  sharpe: number;
  drawdownPct: number;
  benchmark?: {
    name: string;
    returnPct: number;
    annVolPct: number;
  };
}

export interface AttributionItem {
  key: string;
  contributionPct: number;
}

export interface Attribution {
  groupBy: 'security' | 'sector' | 'industry';
  items: AttributionItem[];
  topContributors: string[];
  topDetractors: string[];
}

export interface FactorExposure {
  factor: string;
  beta: number;
}

export interface RiskContribution {
  factor: string;
  pctOfTotalVariance: number;
}

export interface FactorAnalysis {
  asOf: string;
  model: string;
  exposures: FactorExposure[];
  riskContribution: RiskContribution[];
}

export interface VaRAnalysis {
  method: string;
  conf: number;
  horizon: string;
  varAmount: number;
  esAmount: number;
  notes: string;
}

export interface Portfolio {
  id: string;
  name: string;
  total_value?: number;
  daily_pnl?: number;
  daily_return?: number;
  position_count?: number;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// SWR fetcher with error handling
const fetcher = async (url: string) => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  return response.json();
};

// Generate mock data based on portfolio ID
const generateMockSummary = (portfolioId: string, dateRange: { asOf?: string; window?: string }): PortfolioSummary => {
  const seed = portfolioId.length;
  
  // Different mock data based on portfolio type
  const isIndividual = portfolioId === 'a3209353-9ed5-4885-81e8-d4bbc995f96c';
  const isHNW = portfolioId === '14e7f420-b096-4e2e-8cc2-531caf434c05';
  const isHedgeFund = portfolioId === 'cf890da7-7b74-4cb4-acba-2205fdd9dff4';

  let baseData;
  if (isIndividual) {
    baseData = {
      equity: 75000 + Math.sin(seed) * 5000,
      cash: 5000 + Math.cos(seed) * 2000,
      returnPct: 8.5 + Math.sin(seed) * 3,
      annVolPct: 12.3 + Math.cos(seed) * 2,
      sharpe: 1.2 + Math.sin(seed) * 0.3,
      grossExposurePct: 95 + Math.cos(seed) * 5,
      netExposurePct: 94 + Math.sin(seed) * 3
    };
  } else if (isHNW) {
    baseData = {
      equity: 250000 + Math.sin(seed) * 25000,
      cash: 15000 + Math.cos(seed) * 5000,
      returnPct: 12.2 + Math.sin(seed) * 4,
      annVolPct: 16.8 + Math.cos(seed) * 3,
      sharpe: 1.5 + Math.sin(seed) * 0.4,
      grossExposurePct: 110 + Math.cos(seed) * 10,
      netExposurePct: 85 + Math.sin(seed) * 8
    };
  } else {
    baseData = {
      equity: 1500000 + Math.sin(seed) * 100000,
      cash: 50000 + Math.cos(seed) * 15000,
      returnPct: 18.7 + Math.sin(seed) * 6,
      annVolPct: 22.1 + Math.cos(seed) * 4,
      sharpe: 1.8 + Math.sin(seed) * 0.5,
      grossExposurePct: 180 + Math.cos(seed) * 20,
      netExposurePct: 65 + Math.sin(seed) * 15
    };
  }

  return {
    portfolioId,
    asOf: dateRange.asOf || new Date().toISOString().split('T')[0],
    window: dateRange.window || '1m',
    ...baseData,
    longExposurePct: baseData.grossExposurePct * 0.7,
    shortExposurePct: baseData.grossExposurePct * 0.3,
    drawdownPct: -Math.abs(baseData.returnPct * 0.6),
    benchmark: {
      name: 'S&P 500',
      returnPct: 10.5 + Math.cos(seed) * 2,
      annVolPct: 15.2 + Math.sin(seed) * 1.5
    }
  };
};

const generateMockAttribution = (portfolioId: string): Attribution => {
  const isIndividual = portfolioId === 'a3209353-9ed5-4885-81e8-d4bbc995f96c';
  const isHNW = portfolioId === '14e7f420-b096-4e2e-8cc2-531caf434c05';
  
  let topContributors, topDetractors, items;
  
  if (isIndividual) {
    topContributors = ['AAPL', 'MSFT', 'VTI', 'QQQ', 'SPY'];
    topDetractors = ['TSLA', 'META', 'NFLX'];
    items = [
      { key: 'AAPL', contributionPct: 0.0245 },
      { key: 'MSFT', contributionPct: 0.0189 },
      { key: 'VTI', contributionPct: 0.0156 },
      { key: 'TSLA', contributionPct: -0.0087 },
      { key: 'META', contributionPct: -0.0062 }
    ];
  } else if (isHNW) {
    topContributors = ['NVDA', 'GOOGL', 'AMZN', 'BRK.B', 'JPM'];
    topDetractors = ['COIN', 'ARKK', 'PLTR'];
    items = [
      { key: 'NVDA', contributionPct: 0.0387 },
      { key: 'GOOGL', contributionPct: 0.0298 },
      { key: 'AMZN', contributionPct: 0.0234 },
      { key: 'COIN', contributionPct: -0.0156 },
      { key: 'ARKK', contributionPct: -0.0123 }
    ];
  } else {
    topContributors = ['NVDA', 'TSLA', 'AMD', 'NFLX', 'META'];
    topDetractors = ['Short SPY', 'Short QQQ', 'VIX Calls'];
    items = [
      { key: 'NVDA', contributionPct: 0.0543 },
      { key: 'TSLA', contributionPct: 0.0432 },
      { key: 'AMD', contributionPct: 0.0321 },
      { key: 'Short SPY', contributionPct: -0.0287 },
      { key: 'Short QQQ', contributionPct: -0.0198 }
    ];
  }

  return {
    groupBy: 'security',
    items,
    topContributors,
    topDetractors
  };
};

const generateMockFactors = (portfolioId: string): FactorAnalysis => {
  const isIndividual = portfolioId === 'a3209353-9ed5-4885-81e8-d4bbc995f96c';
  const isHNW = portfolioId === '14e7f420-b096-4e2e-8cc2-531caf434c05';
  
  let exposures, riskContribution;
  
  if (isIndividual) {
    exposures = [
      { factor: 'Market Beta', beta: 0.95 },
      { factor: 'Size', beta: -0.12 },
      { factor: 'Value', beta: 0.08 },
      { factor: 'Momentum', beta: 0.15 },
      { factor: 'Quality', beta: 0.22 }
    ];
    riskContribution = [
      { factor: 'Market Beta', pctOfTotalVariance: 65.4 },
      { factor: 'Size', pctOfTotalVariance: 8.7 },
      { factor: 'Quality', pctOfTotalVariance: 12.3 }
    ];
  } else if (isHNW) {
    exposures = [
      { factor: 'Market Beta', beta: 1.15 },
      { factor: 'Size', beta: -0.25 },
      { factor: 'Value', beta: -0.18 },
      { factor: 'Momentum', beta: 0.32 },
      { factor: 'Quality', beta: 0.28 }
    ];
    riskContribution = [
      { factor: 'Market Beta', pctOfTotalVariance: 58.2 },
      { factor: 'Momentum', pctOfTotalVariance: 18.6 },
      { factor: 'Size', pctOfTotalVariance: 11.4 }
    ];
  } else {
    exposures = [
      { factor: 'Market Beta', beta: 0.75 },
      { factor: 'Size', beta: -0.45 },
      { factor: 'Value', beta: -0.32 },
      { factor: 'Momentum', beta: 0.58 },
      { factor: 'Volatility', beta: 0.67 }
    ];
    riskContribution = [
      { factor: 'Market Beta', pctOfTotalVariance: 45.8 },
      { factor: 'Volatility', pctOfTotalVariance: 23.4 },
      { factor: 'Momentum', pctOfTotalVariance: 15.7 }
    ];
  }

  return {
    asOf: new Date().toISOString().split('T')[0],
    model: 'Fama-French 5-Factor',
    exposures,
    riskContribution
  };
};

const generateMockVaR = (portfolioId: string): VaRAnalysis => {
  const seed = portfolioId.length;
  const baseValue = 100000; // Base portfolio value for VaR calculation
  
  return {
    method: 'Historical Simulation',
    conf: 0.99,
    horizon: '1d',
    varAmount: -(baseValue * (0.03 + Math.sin(seed) * 0.01)),
    esAmount: -(baseValue * (0.045 + Math.cos(seed) * 0.015)),
    notes: 'VaR calculated using 252-day historical window'
  };
};

export const usePortfolioContext = (portfolioId?: string) => {
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string | undefined>(portfolioId);
  const [dateRange, setDateRange] = useState<{ asOf?: string; window?: string }>({
    asOf: new Date().toISOString().split('T')[0],
    window: '1m',
  });

  // Fetch all available portfolios from reports endpoint
  const { 
    data: portfolios, 
    error: portfoliosError, 
    isLoading: portfoliosLoading 
  } = useSWR<Portfolio[]>(`${BACKEND_URL}/api/v1/reports/portfolios`, fetcher);

  // Generate mock data for the selected portfolio
  const summary = selectedPortfolioId ? generateMockSummary(selectedPortfolioId, dateRange) : null;
  const attribution = selectedPortfolioId ? generateMockAttribution(selectedPortfolioId) : null;
  const factors = selectedPortfolioId ? generateMockFactors(selectedPortfolioId) : null;
  const varAnalysis = selectedPortfolioId ? generateMockVaR(selectedPortfolioId) : null;

  // Current portfolio selection
  const currentPortfolio = portfolios?.find(p => p.id === selectedPortfolioId);

  // Portfolio context for GPT integration
  const generatePortfolioContext = useCallback(() => {
    if (!selectedPortfolioId || !currentPortfolio) {
      return null;
    }

    const context = {
      portfolio: {
        id: selectedPortfolioId,
        name: currentPortfolio.name,
        total_value: summary?.equity,
        position_count: 15, // Mock position count
      },
      date_range: dateRange,
      summary: summary ? {
        equity: summary.equity,
        cash: summary.cash,
        net_exposure: summary.netExposurePct,
        gross_exposure: summary.grossExposurePct,
        return_pct: summary.returnPct,
        volatility: summary.annVolPct,
        sharpe: summary.sharpe,
        drawdown: summary.drawdownPct,
      } : null,
      attribution: attribution ? {
        top_contributors: attribution.topContributors.slice(0, 5),
        top_detractors: attribution.topDetractors.slice(0, 5),
        items: attribution.items.slice(0, 10),
      } : null,
      factors: factors ? {
        model: factors.model,
        key_exposures: factors.exposures
          .filter(f => Math.abs(f.beta) > 0.1)
          .sort((a, b) => Math.abs(b.beta) - Math.abs(a.beta))
          .slice(0, 10),
      } : null,
      risk: varAnalysis ? {
        var_1d: varAnalysis.varAmount,
        es_1d: varAnalysis.esAmount,
        method: varAnalysis.method,
      } : null,
    };

    return context;
  }, [selectedPortfolioId, currentPortfolio, dateRange, summary, attribution, factors, varAnalysis]);

  // Generate formatted context string for GPT
  const generateContextString = useCallback(() => {
    const context = generatePortfolioContext();
    if (!context) return '';

    let contextString = `PORTFOLIO ANALYSIS CONTEXT:\n`;
    contextString += `Portfolio: ${context.portfolio.name} (ID: ${context.portfolio.id})\n`;
    contextString += `Date Range: ${context.date_range.window} as of ${context.date_range.asOf}\n\n`;

    if (context.summary) {
      contextString += `PORTFOLIO SUMMARY:\n`;
      contextString += `Total Value: $${context.summary.equity.toLocaleString()}\n`;
      contextString += `Net Exposure: ${context.summary.net_exposure.toFixed(1)}%\n`;
      contextString += `Gross Exposure: ${context.summary.gross_exposure.toFixed(1)}%\n`;
      contextString += `Return (${context.date_range.window}): ${context.summary.return_pct.toFixed(2)}%\n`;
      contextString += `Volatility: ${context.summary.volatility.toFixed(1)}%\n`;
      contextString += `Sharpe Ratio: ${context.summary.sharpe.toFixed(2)}\n\n`;
    }

    if (context.attribution) {
      contextString += `TOP CONTRIBUTORS:\n`;
      context.attribution.top_contributors.forEach((contrib, idx) => {
        contextString += `${idx + 1}. ${contrib}\n`;
      });
      contextString += `\nTOP DETRACTORS:\n`;
      context.attribution.top_detractors.forEach((detractor, idx) => {
        contextString += `${idx + 1}. ${detractor}\n`;
      });
      contextString += '\n';
    }

    if (context.factors) {
      contextString += `FACTOR EXPOSURES (${context.factors.model}):\n`;
      context.factors.key_exposures.forEach(factor => {
        contextString += `${factor.factor}: ${factor.beta.toFixed(2)}\n`;
      });
      contextString += '\n';
    }

    if (context.risk) {
      contextString += `RISK METRICS:\n`;
      contextString += `VaR (1-day, 99%): $${context.risk.var_1d.toLocaleString()}\n`;
      contextString += `ES (1-day, 99%): $${context.risk.es_1d.toLocaleString()}\n`;
      contextString += `Method: ${context.risk.method}\n\n`;
    }

    return contextString;
  }, [generatePortfolioContext]);

  // Refresh all data (placeholder since we're using mock data)
  const refreshAll = useCallback(() => {
    // Since we're using mock data, this is a no-op
    console.log('Refresh requested - using mock data');
  }, []);

  // Loading and error states
  const isLoading = portfoliosLoading;
  const hasError = !!portfoliosError;

  return {
    // Portfolio selection
    portfolios: portfolios || [],
    selectedPortfolioId,
    setSelectedPortfolioId,
    currentPortfolio,
    
    // Date/time controls
    dateRange,
    setDateRange,
    
    // Data
    summary,
    attribution,
    factors,
    varAnalysis,
    
    // Context generation
    generatePortfolioContext,
    generateContextString,
    
    // Actions
    refreshAll,
    
    // State
    isLoading,
    hasError,
    error: hasError ? 'Failed to load portfolio data' : null,
  };
};

export default usePortfolioContext;
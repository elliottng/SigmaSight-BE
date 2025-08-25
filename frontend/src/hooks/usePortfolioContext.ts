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

export const usePortfolioContext = (portfolioId?: string) => {
  const [selectedPortfolioId, setSelectedPortfolioId] = useState<string | undefined>(portfolioId);
  const [dateRange, setDateRange] = useState<{ asOf?: string; window?: string }>({
    asOf: new Date().toISOString().split('T')[0],
    window: '1m',
  });

  // Fetch all available portfolios
  const { 
    data: portfolios, 
    error: portfoliosError, 
    isLoading: portfoliosLoading 
  } = useSWR<Portfolio[]>(`${BACKEND_URL}/api/v1/reports/portfolios`, fetcher);

  // Fetch portfolio summary
  const summaryUrl = selectedPortfolioId 
    ? `${BACKEND_URL}/api/v1/portfolio/${selectedPortfolioId}/summary?asOf=${dateRange.asOf}&window=${dateRange.window}`
    : null;
  
  const { 
    data: summary, 
    error: summaryError, 
    isLoading: summaryLoading,
    mutate: mutateSummary
  } = useSWR<PortfolioSummary>(summaryUrl, fetcher);

  // Fetch attribution data
  const attributionUrl = selectedPortfolioId 
    ? `${BACKEND_URL}/api/v1/portfolio/${selectedPortfolioId}/attribution?window=${dateRange.window}&groupBy=security`
    : null;
  
  const { 
    data: attribution, 
    error: attributionError, 
    isLoading: attributionLoading 
  } = useSWR<Attribution>(attributionUrl, fetcher);

  // Fetch factor exposures
  const factorsUrl = selectedPortfolioId 
    ? `${BACKEND_URL}/api/v1/portfolio/${selectedPortfolioId}/factors`
    : null;
  
  const { 
    data: factors, 
    error: factorsError, 
    isLoading: factorsLoading 
  } = useSWR<FactorAnalysis>(factorsUrl, fetcher);

  // Fetch VaR analysis
  const varUrl = selectedPortfolioId 
    ? `${BACKEND_URL}/api/v1/portfolio/${selectedPortfolioId}/risk/var?horizon=1d&conf=0.99&method=historical`
    : null;
  
  const { 
    data: varAnalysis, 
    error: varError, 
    isLoading: varLoading 
  } = useSWR<VaRAnalysis>(varUrl, fetcher);

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
        total_value: currentPortfolio.total_value,
        position_count: currentPortfolio.position_count,
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

  // Refresh all data
  const refreshAll = useCallback(() => {
    mutateSummary();
    // Additional mutate calls would go here for other SWR hooks
  }, [mutateSummary]);

  // Loading and error states
  const isLoading = portfoliosLoading || summaryLoading || attributionLoading || factorsLoading || varLoading;
  const hasError = portfoliosError || summaryError || attributionError || factorsError || varError;

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
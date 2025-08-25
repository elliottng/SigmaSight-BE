'use client';
import { useState, useEffect, useCallback } from 'react';
import useSWR from 'swr';

interface GPTAnalysisRequest {
  portfolio_id: string;
  user_context?: {
    prompt: string;
    selected_positions?: string[];
    date_range?: { from: Date; to: Date };
    page_context?: string;
  };
}

interface GPTHealthStatus {
  status: 'ok' | 'error';
  backend_connected: boolean;
  backend_url?: string;
  error?: string;
}

interface GPTResponse {
  summary_markdown: string;
  machine_readable: {
    snapshot?: { 
      total_value?: number; 
      net_exposure_pct?: number;
      gross_exposure_pct?: number;
      daily_pnl?: number;
    };
    concentration?: { 
      top1?: number; 
      hhi?: number;
      largest_positions?: Array<{ symbol: string; weight: number }>;
    };
    factors?: Array<{ 
      name: string; 
      exposure: number; 
      description?: string; 
    }>;
    gaps: string[];
    actions: string[];
    next_steps?: string[];
  };
  success?: boolean;
  error?: string;
  details?: string;
}

export function useGPTAgent() {
  const [analysis, setAnalysis] = useState<GPTResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Monitor GPT agent health with SWR
  const { data: healthStatus, error: healthError } = useSWR<GPTHealthStatus>(
    '/api/gpt/health',
    async (url) => {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
      }
      return response.json();
    },
    {
      refreshInterval: 30000, // Check every 30 seconds
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
      onError: (err) => {
        console.warn('GPT Agent health check failed:', err);
      }
    }
  );

  const analyze = useCallback(async (request: GPTAnalysisRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/gpt/analyze', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          // Include auth token if available
          ...(typeof window !== 'undefined' && localStorage.getItem('auth_token') && {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          })
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.status} ${response.statusText}`);
      }

      const result: GPTResponse = await response.json();
      
      // Handle GPT agent errors
      if (!result.success && result.error) {
        throw new Error(result.error);
      }

      setAnalysis(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Analysis failed';
      setError(errorMessage);
      console.error('GPT Agent analysis error:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearAnalysis = useCallback(() => {
    setAnalysis(null);
    setError(null);
  }, []);

  // Convenience methods for specific analysis types
  const analyzePortfolio = useCallback(async (portfolioId: string, prompt?: string) => {
    return analyze({
      portfolio_id: portfolioId,
      user_context: {
        prompt: prompt || 'Provide a comprehensive portfolio analysis with key metrics, risks, and recommendations',
        page_context: 'portfolio_overview'
      }
    });
  }, [analyze]);

  const analyzeRisk = useCallback(async (portfolioId: string, selectedPositions?: string[]) => {
    return analyze({
      portfolio_id: portfolioId,
      user_context: {
        prompt: 'Analyze portfolio risk factors, exposures, and potential stress scenarios',
        selected_positions: selectedPositions,
        page_context: 'risk_analysis'
      }
    });
  }, [analyze]);

  const analyzePositions = useCallback(async (portfolioId: string, selectedPositions: string[]) => {
    return analyze({
      portfolio_id: portfolioId,
      user_context: {
        prompt: `Analyze the selected positions for risk, correlation, and optimization opportunities`,
        selected_positions: selectedPositions,
        page_context: 'position_analysis'
      }
    });
  }, [analyze]);

  // Derived state
  const isOnline = healthStatus?.backend_connected && healthStatus?.status === 'ok';
  const hasHealthError = !!healthError || healthStatus?.status === 'error';

  return {
    // Main analysis function
    analyze,
    
    // Convenience methods
    analyzePortfolio,
    analyzeRisk,
    analyzePositions,
    
    // State
    analysis,
    loading,
    error,
    
    // Health monitoring
    healthStatus,
    isOnline,
    hasHealthError,
    
    // Utilities
    clearAnalysis
  };
}

// Export types for use in components
export type { GPTAnalysisRequest, GPTResponse, GPTHealthStatus };
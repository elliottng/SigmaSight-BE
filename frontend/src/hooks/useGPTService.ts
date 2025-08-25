import { useState, useCallback } from 'react';

// GPT Service Types
export interface GPTResponse {
  summary_markdown?: string;
  machine_readable?: {
    snapshot?: {
      total_value?: number;
      net_exposure_pct?: number;
      gross_exposure_pct?: number;
      daily_pnl?: number;
    };
    concentration?: {
      top1?: number;
      hhi?: number;
      largest_positions?: Array<{ symbol: string; weight: number; }>;
    };
    factors?: Array<{
      name: string;
      exposure: number;
      description?: string;
    }>;
    gaps?: string[];
    actions?: string[];
    next_steps?: string[];
  };
  success?: boolean;
  response?: string; // For direct integration backward compatibility
}

export interface GPTRequest {
  message: string;
  portfolio_id?: string;
  context?: {
    selected_positions?: string[];
    date_range?: { from: Date; to: Date };
    page_context?: 'portfolio_overview' | 'risk_analysis' | 'chat_page';
    view?: 'portfolio' | 'longs' | 'shorts';
    group_by?: 'security' | 'sector' | 'factor';
  };
}

export type GPTServiceMode = 'direct' | 'agent';

export interface UseGPTServiceOptions {
  mode?: GPTServiceMode;
  defaultPortfolioId?: string;
}

export const useGPTService = (options: UseGPTServiceOptions = {}) => {
  const { mode = 'direct', defaultPortfolioId } = options;
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Environment-based service URL detection
  const getServiceUrl = useCallback(() => {
    if (mode === 'agent') {
      return process.env.NEXT_PUBLIC_GPT_AGENT_URL || 'http://localhost:8787';
    }
    return '/api/gpt'; // Direct integration via Next.js API routes
  }, [mode]);

  // Flexible analyze function supporting both modes
  const analyzeWithGPT = useCallback(async (request: GPTRequest): Promise<GPTResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const serviceUrl = getServiceUrl();
      
      if (mode === 'agent') {
        // GPT Agent Service Integration
        const response = await fetch(`${serviceUrl}/analyze`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            // JWT token will be added here when authentication is implemented
          },
          body: JSON.stringify({
            portfolio_id: request.portfolio_id || defaultPortfolioId,
            user_context: {
              prompt: request.message,
              ...request.context,
            },
          }),
        });

        if (!response.ok) {
          throw new Error(`GPT Agent service error: ${response.status}`);
        }

        const data = await response.json();
        return data;
      } else {
        // Direct Integration (Current Working Mode)
        const response = await fetch(`${serviceUrl}/analyze`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: request.message,
            portfolio_id: request.portfolio_id || defaultPortfolioId,
            context: request.context,
          }),
        });

        if (!response.ok) {
          throw new Error(`Direct GPT service error: ${response.status}`);
        }

        const data = await response.json();
        
        // Transform direct response to match GPT agent format for consistency
        return {
          summary_markdown: data.response || data.summary_markdown,
          machine_readable: data.machine_readable || {},
          success: true,
        };
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown GPT service error';
      setError(errorMessage);
      console.error('GPT Service Error:', err);
      
      // Return error response in consistent format
      return {
        success: false,
        summary_markdown: `Error: ${errorMessage}`,
        machine_readable: {
          gaps: ['gpt_service_unavailable'],
        },
      };
    } finally {
      setIsLoading(false);
    }
  }, [mode, defaultPortfolioId, getServiceUrl]);

  // Convenience methods for common analysis types
  const analyzePortfolio = useCallback((portfolioId: string, prompt?: string) => {
    return analyzeWithGPT({
      message: prompt || 'Provide a comprehensive portfolio analysis including risk metrics, factor exposures, and key insights.',
      portfolio_id: portfolioId,
      context: {
        page_context: 'portfolio_overview',
        view: 'portfolio',
      },
    });
  }, [analyzeWithGPT]);

  const analyzeRisk = useCallback((portfolioId: string, prompt?: string) => {
    return analyzeWithGPT({
      message: prompt || 'Analyze portfolio risk including VaR, factor exposures, concentration risks, and stress testing insights.',
      portfolio_id: portfolioId,
      context: {
        page_context: 'risk_analysis',
        view: 'portfolio',
      },
    });
  }, [analyzeWithGPT]);

  const analyzePositions = useCallback((portfolioId: string, selectedPositions: string[], prompt?: string) => {
    return analyzeWithGPT({
      message: prompt || `Analyze the following positions: ${selectedPositions.join(', ')}`,
      portfolio_id: portfolioId,
      context: {
        selected_positions: selectedPositions,
        page_context: 'portfolio_overview',
      },
    });
  }, [analyzeWithGPT]);

  // Health check for service availability
  const checkServiceHealth = useCallback(async () => {
    try {
      const serviceUrl = getServiceUrl();
      
      if (mode === 'agent') {
        const response = await fetch(`${serviceUrl}/health`);
        return response.ok;
      } else {
        // For direct mode, health is determined by API route availability
        const response = await fetch('/api/gpt/health', { method: 'HEAD' });
        return response.ok;
      }
    } catch {
      return false;
    }
  }, [mode, getServiceUrl]);

  return {
    // Core functionality
    analyzeWithGPT,
    
    // Convenience methods
    analyzePortfolio,
    analyzeRisk,
    analyzePositions,
    
    // Service management
    checkServiceHealth,
    
    // State
    isLoading,
    error,
    mode,
    
    // Service info
    serviceUrl: getServiceUrl(),
  };
};

export default useGPTService;
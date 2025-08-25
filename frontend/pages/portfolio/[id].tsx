import { useRouter } from 'next/router';
import { useState } from 'react';
import usePortfolioContext from '../../src/hooks/usePortfolioContext';
import useGPTService from '../../src/hooks/useGPTService';
import Link from 'next/link';

export default function PortfolioPage() {
  const router = useRouter();
  const { id } = router.query;
  const portfolioId = typeof id === 'string' ? id : undefined;

  const {
    portfolios,
    currentPortfolio,
    summary,
    attribution,
    factors,
    varAnalysis,
    dateRange,
    setDateRange,
    generateContextString,
    isLoading,
    hasError,
  } = usePortfolioContext(portfolioId);

  const {
    analyzePortfolio,
    isLoading: gptLoading,
    error: gptError,
  } = useGPTService({ mode: 'direct', defaultPortfolioId: portfolioId });

  const [gptResponse, setGptResponse] = useState<any>(null);

  const handleGPTAnalysis = async () => {
    if (!portfolioId) return;
    
    try {
      const response = await analyzePortfolio(
        portfolioId,
        'Provide a comprehensive analysis of this portfolio including key insights, risk assessment, and actionable recommendations.'
      );
      setGptResponse(response);
    } catch (error) {
      console.error('GPT analysis failed:', error);
    }
  };

  if (!portfolioId) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Invalid Portfolio</h1>
          <Link href="/" className="text-blue-600 hover:text-blue-800">
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading portfolio data...</p>
        </div>
      </div>
    );
  }

  if (hasError || !currentPortfolio) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-900 mb-4">Portfolio Not Found</h1>
          <p className="text-gray-600 mb-4">Unable to load portfolio data.</p>
          <Link href="/" className="text-blue-600 hover:text-blue-800">
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <Link href="/" className="text-blue-600 hover:text-blue-800 text-sm">
                ← Dashboard
              </Link>
              <h1 className="text-3xl font-bold text-gray-900 mt-2">
                {currentPortfolio.name}
              </h1>
              <p className="text-gray-500">Portfolio ID: {portfolioId}</p>
            </div>
            
            {/* Date Range Controls */}
            <div className="flex items-center space-x-4">
              <select 
                value={dateRange.window} 
                onChange={(e) => setDateRange(prev => ({ ...prev, window: e.target.value }))}
                className="border border-gray-300 rounded-md px-3 py-2 bg-white"
              >
                <option value="1d">1 Day</option>
                <option value="1w">1 Week</option>
                <option value="1m">1 Month</option>
                <option value="3m">3 Months</option>
                <option value="6m">6 Months</option>
                <option value="1y">1 Year</option>
              </select>
              
              <input
                type="date"
                value={dateRange.asOf}
                onChange={(e) => setDateRange(prev => ({ ...prev, asOf: e.target.value }))}
                className="border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Portfolio Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Total Equity</h3>
              <p className="text-2xl font-bold text-gray-900">
                ${summary.equity.toLocaleString()}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                Cash: ${summary.cash.toLocaleString()}
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Net Exposure</h3>
              <p className="text-2xl font-bold text-gray-900">
                {summary.netExposurePct.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600 mt-1">
                Gross: {summary.grossExposurePct.toFixed(1)}%
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Return ({dateRange.window})</h3>
              <p className={`text-2xl font-bold ${summary.returnPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {summary.returnPct > 0 ? '+' : ''}{summary.returnPct.toFixed(2)}%
              </p>
              <p className="text-sm text-gray-600 mt-1">
                Sharpe: {summary.sharpe.toFixed(2)}
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-medium text-gray-500">Volatility</h3>
              <p className="text-2xl font-bold text-gray-900">
                {summary.annVolPct.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600 mt-1">
                Max DD: {summary.drawdownPct.toFixed(1)}%
              </p>
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Attribution Analysis */}
          {attribution && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Performance Attribution</h2>
              
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Top Contributors</h3>
                <div className="space-y-2">
                  {attribution.topContributors.slice(0, 5).map((contributor, idx) => (
                    <div key={contributor} className="flex justify-between items-center">
                      <span className="text-sm font-medium">{contributor}</span>
                      <span className="text-sm text-green-600">#{idx + 1}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Top Detractors</h3>
                <div className="space-y-2">
                  {attribution.topDetractors.slice(0, 5).map((detractor, idx) => (
                    <div key={detractor} className="flex justify-between items-center">
                      <span className="text-sm font-medium">{detractor}</span>
                      <span className="text-sm text-red-600">#{idx + 1}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Factor Exposures */}
          {factors && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Factor Exposures</h2>
              <p className="text-sm text-gray-600 mb-4">Model: {factors.model}</p>
              
              <div className="space-y-3">
                {factors.exposures
                  .filter(factor => Math.abs(factor.beta) > 0.05)
                  .sort((a, b) => Math.abs(b.beta) - Math.abs(a.beta))
                  .slice(0, 8)
                  .map((factor) => (
                  <div key={factor.factor} className="flex items-center">
                    <div className="w-24 text-sm font-medium text-gray-700 truncate">
                      {factor.factor}
                    </div>
                    <div className="flex-1 mx-3">
                      <div className="relative">
                        <div className="h-2 bg-gray-200 rounded">
                          <div 
                            className={`h-2 rounded ${factor.beta >= 0 ? 'bg-blue-500' : 'bg-red-500'}`}
                            style={{ 
                              width: `${Math.min(Math.abs(factor.beta) * 100, 100)}%`,
                              marginLeft: factor.beta < 0 ? `${100 - Math.min(Math.abs(factor.beta) * 100, 100)}%` : '0'
                            }}
                          />
                        </div>
                      </div>
                    </div>
                    <div className={`w-16 text-sm font-medium text-right ${factor.beta >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
                      {factor.beta.toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Risk Analysis */}
          {varAnalysis && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Risk Analysis</h2>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500">VaR (1-day, 99%)</h3>
                  <p className="text-xl font-bold text-red-600">
                    ${Math.abs(varAnalysis.varAmount).toLocaleString()}
                  </p>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-500">Expected Shortfall</h3>
                  <p className="text-xl font-bold text-red-600">
                    ${Math.abs(varAnalysis.esAmount).toLocaleString()}
                  </p>
                </div>
              </div>
              
              <div className="mt-4">
                <p className="text-sm text-gray-600">
                  Method: {varAnalysis.method}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  {varAnalysis.notes}
                </p>
              </div>
            </div>
          )}

          {/* GPT Analysis */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">AI Analysis</h2>
              <button
                onClick={handleGPTAnalysis}
                disabled={gptLoading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
              >
                {gptLoading ? 'Analyzing...' : 'Analyze Portfolio'}
              </button>
            </div>
            
            {gptError && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
                <p className="text-red-800 text-sm">Error: {gptError}</p>
              </div>
            )}
            
            {gptResponse && (
              <div className="space-y-4">
                <div className="prose text-sm">
                  <p className="whitespace-pre-wrap">{gptResponse.summary_markdown || gptResponse.response}</p>
                </div>
                
                {gptResponse.machine_readable?.actions && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Recommended Actions</h4>
                    <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                      {gptResponse.machine_readable.actions.map((action: string, idx: number) => (
                        <li key={idx}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
            
            {!gptResponse && !gptError && (
              <div className="text-center text-gray-500 py-8">
                <p className="text-sm">Click "Analyze Portfolio" to get AI insights about this portfolio's performance, risk profile, and recommendations.</p>
              </div>
            )}
          </div>
        </div>

        {/* Raw Portfolio Context (for debugging) */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Portfolio Context</h2>
          <pre className="bg-gray-100 p-4 rounded-md text-xs overflow-auto max-h-96">
            {generateContextString() || 'No context available'}
          </pre>
        </div>
      </div>
    </div>
  );
}
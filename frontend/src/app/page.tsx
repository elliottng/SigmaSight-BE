'use client';

import React, { useState, useEffect } from 'react';
import MetricCard from '@/components/ui/MetricCard';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface Portfolio {
  id: string;
  name: string;
  total_value?: number;
  daily_pnl?: number;
  daily_return?: number;
  position_count?: number;
  report_folder?: string;
  generated_date?: string;
  formats_available?: string[];
}

export default function Dashboard() {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [reportContent, setReportContent] = useState<string | null>(null);
  const [reportFormat, setReportFormat] = useState<string>('json');

  useEffect(() => {
    fetchPortfolios();
  }, []);

  const fetchPortfolios = async () => {
    try {
      setLoading(true);
      
      // Fetch real portfolio data from the reports API
      const portfoliosResponse = await fetch('http://localhost:8000/api/v1/reports/portfolios');
      
      if (!portfoliosResponse.ok) {
        throw new Error(`API error: ${portfoliosResponse.status}`);
      }
      
      const portfoliosData = await portfoliosResponse.json();
      console.log('Portfolio data:', portfoliosData);
      
      // Transform the data to match our interface
      const transformedPortfolios = portfoliosData.map((portfolio: any) => ({
        id: portfolio.id,
        name: portfolio.name,
        total_value: Math.random() * 300000 + 50000, // Mock values for now
        daily_pnl: (Math.random() - 0.5) * 10000,
        daily_return: (Math.random() - 0.5) * 0.05,
        position_count: Math.floor(Math.random() * 20) + 5,
        report_folder: portfolio.report_folder,
        generated_date: portfolio.generated_date,
        formats_available: portfolio.formats_available
      }));
      
      setPortfolios(transformedPortfolios);
      setError(null);
    } catch (err) {
      console.error('Error fetching portfolios:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch portfolios');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value?: number) => {
    if (typeof value !== 'number') return '--';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatPercent = (value?: number) => {
    if (typeof value !== 'number') return '--';
    return `${(value * 100).toFixed(2)}%`;
  };

  const fetchReportContent = async (portfolio: Portfolio, format: string) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/reports/portfolio/${portfolio.id}/content/${format}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to fetch ${format} report`);
      }
      
      const data = await response.json();
      return data.content;
    } catch (err) {
      console.error('Error fetching report:', err);
      return `Error loading ${format} report: ${err instanceof Error ? err.message : 'Unknown error'}`;
    }
  };

  const handleViewReport = async (portfolio: Portfolio) => {
    setSelectedPortfolio(portfolio);
    setLoading(true);
    
    // Try to fetch JSON format first, fallback to first available format
    const format = portfolio.formats_available?.includes('json') 
      ? 'json' 
      : portfolio.formats_available?.[0] || 'md';
    
    setReportFormat(format);
    const content = await fetchReportContent(portfolio, format);
    setReportContent(content);
    setLoading(false);
  };

  const handleBackToDashboard = () => {
    setSelectedPortfolio(null);
    setReportContent(null);
  };

  const handleFormatChange = async (newFormat: string) => {
    if (!selectedPortfolio) return;
    
    setLoading(true);
    setReportFormat(newFormat);
    const content = await fetchReportContent(selectedPortfolio, newFormat);
    setReportContent(content);
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Report View */}
        {selectedPortfolio ? (
          <>
            {/* Report Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={handleBackToDashboard}
                  className="btn-secondary"
                >
                  ← Back to Dashboard
                </button>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">{selectedPortfolio.name}</h1>
                  <p className="text-gray-600 mt-2">Portfolio Report - Generated {selectedPortfolio.generated_date}</p>
                </div>
              </div>
              
              {/* Format Selector */}
              {selectedPortfolio.formats_available && selectedPortfolio.formats_available.length > 1 && (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">Format:</span>
                  <select
                    value={reportFormat}
                    onChange={(e) => handleFormatChange(e.target.value)}
                    className="border border-gray-300 rounded-md px-3 py-1 text-sm"
                  >
                    {selectedPortfolio.formats_available.map((format) => (
                      <option key={format} value={format}>
                        {format.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* Report Content */}
            <div className="card">
              {loading ? (
                <div className="flex justify-center py-12">
                  <LoadingSpinner />
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-between border-b pb-3">
                    <h2 className="text-xl font-semibold">Portfolio Report ({reportFormat.toUpperCase()})</h2>
                    <span className="text-sm text-gray-500">
                      {reportContent?.length || 0} characters
                    </span>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-auto">
                    <pre className="text-sm font-mono whitespace-pre-wrap break-words">
                      {reportContent || 'No content available'}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </>
        ) : (
          <>
            {/* Dashboard Header */}
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Portfolio Dashboard</h1>
                <p className="text-gray-600 mt-2">Monitor your portfolio performance and risk metrics</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Last Updated</p>
                <p className="text-lg font-semibold">{new Date().toLocaleTimeString()}</p>
              </div>
            </div>

            {/* Loading State */}
            {loading && (
              <div className="flex justify-center py-12">
                <LoadingSpinner />
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <div className="text-red-600">
                    <h3 className="text-lg font-medium">Connection Error</h3>
                    <p className="mt-1 text-sm">{error}</p>
                    <p className="mt-2 text-sm">Make sure the backend server is running on http://localhost:8000</p>
                  </div>
                </div>
              </div>
            )}

            {/* Portfolio Summary Cards */}
            {!loading && !error && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <MetricCard
                    title="Total Portfolios"
                    value={portfolios.length.toString()}
                    subtitle="Active portfolios"
                  />
                  <MetricCard
                    title="Combined Value"
                    value={formatCurrency(
                      portfolios.reduce((sum, p) => sum + (p.total_value || 0), 0)
                    )}
                    subtitle="Total across all portfolios"
                  />
                  <MetricCard
                    title="Total Positions"
                    value={portfolios.reduce((sum, p) => sum + (p.position_count || 0), 0).toString()}
                    subtitle="Active positions"
                  />
                  <MetricCard
                    title="Backend Status"
                    value="Connected"
                    subtitle="API operational"
                    trend="positive"
                  />
                </div>

                {/* Portfolio List */}
                <div className="space-y-6">
                  <h2 className="text-2xl font-bold text-gray-900">Your Portfolios</h2>
                  
                  {portfolios.length === 0 ? (
                    <div className="text-center py-12">
                      <p className="text-gray-500 text-lg">No portfolios found</p>
                      <p className="text-gray-400 text-sm mt-2">Create your first portfolio to get started</p>
                    </div>
                  ) : (
                    <div className="grid gap-6">
                      {portfolios.map((portfolio) => (
                        <div key={portfolio.id} className="card hover:shadow-md transition-shadow">
                          <div className="flex items-center justify-between">
                            <div>
                              <h3 className="text-xl font-semibold text-gray-900">{portfolio.name}</h3>
                              <p className="text-gray-500 text-sm">ID: {portfolio.id}</p>
                              {portfolio.formats_available && (
                                <p className="text-gray-400 text-xs mt-1">
                                  Available formats: {portfolio.formats_available.join(', ').toUpperCase()}
                                </p>
                              )}
                            </div>
                            <div className="text-right">
                              <p className="text-2xl font-bold text-gray-900">
                                {formatCurrency(portfolio.total_value)}
                              </p>
                              <div className="flex items-center space-x-4 text-sm">
                                <span className="text-gray-500">
                                  Daily P&L: {formatCurrency(portfolio.daily_pnl)}
                                </span>
                                <span className={`${
                                  (portfolio.daily_return || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                  {formatPercent(portfolio.daily_return)}
                                </span>
                              </div>
                            </div>
                          </div>
                          
                          <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
                            <span>{portfolio.position_count || 0} positions</span>
                            <button 
                              onClick={() => handleViewReport(portfolio)}
                              className="btn-primary text-sm"
                            >
                              View Report
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
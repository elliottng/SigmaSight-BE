'use client';

import { Card } from '@/components/ui/Card';
import MetricCard from '@/components/ui/MetricCard';
import { formatCurrency, formatPercent } from '@/lib/utils';

interface PortfolioOverviewProps {
  portfolio: any;
  performance: any;
}

export function PortfolioOverview({ portfolio, performance }: PortfolioOverviewProps) {
  if (!portfolio) {
    return (
      <Card className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </Card>
    );
  }

  const metrics = [
    {
      title: 'Total Value',
      value: formatCurrency(portfolio.total_value || 0),
      subtitle: performance?.total_return_pct ? formatPercent(performance.total_return_pct) : undefined,
      trend: performance?.total_return_pct > 0 ? 'positive' : performance?.total_return_pct < 0 ? 'negative' : 'neutral'
    },
    {
      title: 'Net Exposure',
      value: formatPercent(portfolio.net_exposure_pct || 0),
      subtitle: 'Long - Short positions'
    },
    {
      title: 'Gross Exposure', 
      value: formatPercent(portfolio.gross_exposure_pct || 0),
      subtitle: 'Total position size'
    },
    {
      title: 'Daily P&L',
      value: formatCurrency(portfolio.daily_pnl || 0),
      subtitle: portfolio.daily_pnl_pct ? formatPercent(portfolio.daily_pnl_pct) : undefined,
      trend: portfolio.daily_pnl > 0 ? 'positive' : portfolio.daily_pnl < 0 ? 'negative' : 'neutral'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Portfolio Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map((metric, index) => (
            <MetricCard
              key={index}
              title={metric.title}
              value={metric.value}
              trend={metric.trend}
              subtitle={metric.subtitle}
            />
          ))}
        </div>
      </Card>

      {/* Additional Portfolio Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Details</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Created:</span>
              <span className="font-medium">
                {portfolio.created_at ? new Date(portfolio.created_at).toLocaleDateString() : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Last Updated:</span>
              <span className="font-medium">
                {portfolio.updated_at ? new Date(portfolio.updated_at).toLocaleDateString() : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Positions:</span>
              <span className="font-medium">{portfolio.position_count || 0}</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Beta:</span>
              <span className="font-medium">{portfolio.beta?.toFixed(2) || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Volatility:</span>
              <span className="font-medium">
                {portfolio.volatility ? formatPercent(portfolio.volatility) : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Sharpe Ratio:</span>
              <span className="font-medium">{portfolio.sharpe_ratio?.toFixed(2) || 'N/A'}</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

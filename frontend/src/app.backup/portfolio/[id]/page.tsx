'use client';

import { useParams } from 'next/navigation';
import { PortfolioOverview } from '@/components/portfolio/PortfolioOverview';
import { PositionsTable } from '@/components/portfolio/PositionsTable';
import { usePortfolioData } from '@/hooks/usePortfolioData';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { Card } from '@/components/ui/Card';
import { GPTToolbar } from '@/components/gpt/GPTToolbar';

export default function PortfolioDetailPage() {
  const params = useParams();
  const portfolioId = params.id as string;
  
  const { portfolio, positions, performance, isLoading, error } = usePortfolioData(portfolioId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="p-6">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Error Loading Portfolio</h1>
          <p className="text-gray-600">{error.message || 'Failed to load portfolio data'}</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      {/* Portfolio Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {portfolio?.name || 'Portfolio Details'}
          </h1>
          <p className="text-gray-600 mt-1">
            Portfolio ID: {portfolioId}
          </p>
        </div>
      </div>

      {/* Portfolio Overview Section */}
      <PortfolioOverview 
        portfolio={portfolio}
        performance={performance}
      />

      {/* Positions Table Section */}
      <div className="space-y-4">
        <h2 className="text-2xl font-semibold text-gray-900">Positions</h2>
        <PositionsTable 
          positions={positions}
          portfolioId={portfolioId}
        />
      </div>

      {/* GPT Toolbar */}
      <GPTToolbar portfolioId={portfolioId} />
    </div>
  );
}

import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export function usePortfolioData(portfolioId: string) {
  const { data: summary, error: summaryError } = useSWR(
    portfolioId ? `/api/portfolio/${portfolioId}/summary` : null,
    fetcher
  );

  const { data: positions, error: positionsError } = useSWR(
    portfolioId ? `/api/portfolio/${portfolioId}/positions` : null,
    fetcher
  );

  const { data: performance, error: performanceError } = useSWR(
    portfolioId ? `/api/portfolio/${portfolioId}/performance` : null,
    fetcher
  );

  const isLoading = !summary || !positions;
  const error = summaryError || positionsError || performanceError;

  return {
    portfolio: summary,
    positions: positions || [],
    performance: performance,
    isLoading,
    error,
  };
}

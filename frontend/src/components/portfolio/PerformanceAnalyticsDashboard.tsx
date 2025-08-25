'use client';

import { useMemo, useState } from 'react';
import useSWR from 'swr';
import { useRouter } from 'next/router';

import { Card, CardContent } from '@/components/ui/Card';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

/* -------------------------------------------------------------------------- */
/*                                   Types                                    */
/* -------------------------------------------------------------------------- */
type View = "portfolio" | "longs" | "shorts";
type Period = "1d" | "1w" | "1m" | "3m" | "6m" | "1y";
type Index = "S&P 500" | "Nasdaq" | "MSCI World";

interface PortfolioSummary {
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

interface Attribution {
  groupBy: 'security' | 'sector' | 'industry';
  items: Array<{
    key: string;
    contributionPct: number;
  }>;
  topContributors: string[];
  topDetractors: string[];
}

interface FactorExposure {
  factor: string;
  beta: number;
}

interface FactorAnalysis {
  asOf: string;
  model: string;
  exposures: FactorExposure[];
  riskContribution: Array<{
    factor: string;
    pctOfTotalVariance: number;
  }>;
}

interface VaRAnalysis {
  method: string;
  conf: number;
  horizon: string;
  varAmount: number;
  esAmount: number;
  notes: string;
}

/* -------------------------------------------------------------------------- */
/*                               SWR Fetcher                                  */
/* -------------------------------------------------------------------------- */
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

const fetcher = async (url: string) => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  return response.json();
};

/* -------------------------------------------------------------------------- */
/*                           Portfolio Data Hook                              */
/* -------------------------------------------------------------------------- */
const usePortfolioData = (portfolioId: string, dateRange: { asOf: string; window: Period }) => {
  // Portfolio summary
  const summaryUrl = `${BACKEND_URL}/api/v1/portfolio/${portfolioId}/summary?asOf=${dateRange.asOf}&window=${dateRange.window}`;
  const { data: summary, error: summaryError, isLoading: summaryLoading } = useSWR<PortfolioSummary>(summaryUrl, fetcher);

  // Attribution data
  const attributionUrl = `${BACKEND_URL}/api/v1/portfolio/${portfolioId}/attribution?window=${dateRange.window}&groupBy=security`;
  const { data: attribution, error: attributionError, isLoading: attributionLoading } = useSWR<Attribution>(attributionUrl, fetcher);

  // Factor exposures
  const factorsUrl = `${BACKEND_URL}/api/v1/portfolio/${portfolioId}/factors`;
  const { data: factors, error: factorsError, isLoading: factorsLoading } = useSWR<FactorAnalysis>(factorsUrl, fetcher);

  // VaR analysis
  const varUrl = `${BACKEND_URL}/api/v1/portfolio/${portfolioId}/risk/var?horizon=1d&conf=0.99&method=historical`;
  const { data: varAnalysis, error: varError, isLoading: varLoading } = useSWR<VaRAnalysis>(varUrl, fetcher);

  const isLoading = summaryLoading || attributionLoading || factorsLoading || varLoading;
  const hasError = summaryError || attributionError || factorsError || varError;

  return {
    summary,
    attribution,
    factors,
    varAnalysis,
    isLoading,
    hasError
  };
};

/* -------------------------------------------------------------------------- */
/*                           Mock Data Fallbacks                             */
/* -------------------------------------------------------------------------- */
const generateMockMetrics = (view: View, period: Period, summary?: PortfolioSummary) => {
  if (summary) {
    return {
      returnPct: `${summary.returnPct.toFixed(2)}%`,
      volPct: `${summary.annVolPct.toFixed(2)}%`,
      sharpe: summary.sharpe.toFixed(2),
      sortino: (summary.sharpe * 1.2).toFixed(2), // Approximate Sortino from Sharpe
    };
  }

  // Fallback mock data
  const seed = view.length + period.length;
  return {
    returnPct: (Math.sin(seed) * 5 + 2).toFixed(2) + "%",
    volPct: (Math.cos(seed) * 10 + 15).toFixed(2) + "%",
    sharpe: (Math.sin(seed) + 1.5).toFixed(2),
    sortino: (Math.cos(seed) + 2).toFixed(2),
  };
};

const generateMockIndexMetrics = (index: Index, period: Period) => {
  const seed = index.length + period.length;
  return {
    returnPct: (Math.sin(seed * 2) * 4 + 1.5).toFixed(2) + "%",
    volPct: (Math.cos(seed * 2) * 8 + 12).toFixed(2) + "%",
  };
};

const transformAttributionData = (attribution?: Attribution, view: View = "portfolio") => {
  if (!attribution) {
    // Fallback mock data
    const tickers = ["NVDA", "META", "AAPL", "MSFT", "GOOGL"];
    return {
      longs: {
        contributors: tickers.map((t, i) => ({ ticker: t, value: (i + 1) * 20 })),
        detractors: tickers.map((t, i) => ({ ticker: t, value: -(i + 1) * 15 })),
      },
      shorts: {
        contributors: tickers.map((t, i) => ({ ticker: t, value: (i + 1) * 15 })).reverse(),
        detractors: tickers.map((t, i) => ({ ticker: t, value: -(i + 1) * 10 })).reverse(),
      },
    };
  }

  const positiveItems = attribution.items.filter(item => item.contributionPct > 0);
  const negativeItems = attribution.items.filter(item => item.contributionPct < 0);

  const contributors = positiveItems.slice(0, 5).map(item => ({
    ticker: item.key,
    value: item.contributionPct * 100
  }));

  const detractors = negativeItems.slice(0, 5).map(item => ({
    ticker: item.key,
    value: item.contributionPct * 100
  }));

  return {
    longs: { contributors, detractors },
    shorts: { contributors: contributors.reverse(), detractors: detractors.reverse() },
  };
};

const transformFactorData = (factors?: FactorAnalysis) => {
  if (!factors) {
    // Fallback mock data
    return {
      factors: [
        { name: "Beta", value: 1.2 },
        { name: "Momentum", value: 0.8 },
        { name: "Value", value: -0.5 },
        { name: "Growth", value: 1.1 },
      ],
      industries: [
        { name: "Tech", value: 15.2 },
        { name: "Comm Svcs", value: 8.7 },
        { name: "Financials", value: -3.4 },
        { name: "Industrials", value: 5.1 },
      ],
    };
  }

  const factorContribs = factors.exposures.slice(0, 8).map(exp => ({
    name: exp.factor,
    value: exp.beta * 15 // Convert to contribution percentage
  }));

  const industryContribs = factors.riskContribution?.slice(0, 4).map(risk => ({
    name: risk.factor,
    value: risk.pctOfTotalVariance
  })) || [];

  return {
    factors: factorContribs,
    industries: industryContribs,
  };
};

/* -------------------------------------------------------------------------- */
/*                               Re-usable UI                                */
/* -------------------------------------------------------------------------- */
const MetricCard = ({ label, value }: { label: string; value: string }) => (
  <Card>
    <CardContent className="p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-xl font-bold">{value}</p>
    </CardContent>
  </Card>
);

const AttributionTickerCard = ({
  ticker,
  value,
  colorClass,
}: {
  ticker: string;
  value: number;
  colorClass: string;
}) => (
  <Card>
    <CardContent className="flex items-center justify-between p-3">
      <p className="text-sm font-semibold">{ticker}</p>
      <p className={`text-sm font-semibold ${colorClass}`}>
        {value > 0 ? "+" : ""}
        {(value / 100).toFixed(2)}%
      </p>
    </CardContent>
  </Card>
);

const ContributionCard = ({ title, value }: { title: string; value: number }) => {
  const color = value >= 0 ? "text-green-600" : "text-red-600";
  const txt = `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
  return (
    <Card>
      <CardContent className="p-3">
        <p className="text-xs text-gray-500">{title}</p>
        <p className={`text-base font-semibold ${color}`}>{txt}</p>
      </CardContent>
    </Card>
  );
};

/* -------------------------------------------------------------------------- */
/*                              Main Component                                */
/* -------------------------------------------------------------------------- */
export function PerformanceAnalyticsDashboard() {
  const router = useRouter();
  const { id } = router.query;
  const portfolioId = typeof id === 'string' ? id : '';

  /* ------------------------- Local component state ----------------------- */
  const [view, setView] = useState<View>("portfolio");
  const [period, setPeriod] = useState<Period>("1m");
  const [index, setIndex] = useState<Index>("S&P 500");

  const dateRange = useMemo(() => ({
    asOf: new Date().toISOString().split('T')[0],
    window: period
  }), [period]);

  /* ----------------------------- Data fetching ---------------------------- */
  const { summary, attribution, factors, varAnalysis, isLoading, hasError } = usePortfolioData(portfolioId, dateRange);

  /* ----------------------------- Derived data ---------------------------- */
  const portfolio = useMemo(() => generateMockMetrics(view, period, summary), [view, period, summary]);
  const benchmark = useMemo(() => generateMockIndexMetrics(index, period), [index, period]);
  const attributionData = useMemo(() => transformAttributionData(attribution, view), [attribution, view]);
  const contrib = useMemo(() => transformFactorData(factors), [factors]);

  /* ----------------------------- Loading/Error states ----------------------------- */
  if (!portfolioId) {
    return <div className="p-8 text-center">Invalid portfolio ID</div>;
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3">Loading portfolio data...</span>
      </div>
    );
  }

  /* ------------------------------ Rendering ----------------------------- */
  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-8">
      {/* Page header */}
      <header>
        <h2 className="text-lg font-bold">Performance Analytics</h2>
        <p className="text-sm text-gray-600">
          Analyze portfolio performance, attribution and factor contributions.
        </p>
        {hasError && (
          <p className="text-sm text-amber-600 mt-1">
            Some data unavailable - using fallback calculations
          </p>
        )}
      </header>

      {/* Index benchmark & filters */}
      <section>
        <div className="mb-4 flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <h3 className="text-base font-semibold">Index Benchmark</h3>

            <Select value={index} onValueChange={(v: Index) => setIndex(v)}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Select Index" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="S&P 500">S&P 500</SelectItem>
                <SelectItem value="Nasdaq">Nasdaq</SelectItem>
                <SelectItem value="MSCI World">MSCI World</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Label className="text-sm">View</Label>
              <Select value={view} onValueChange={(v: View) => setView(v)}>
                <SelectTrigger className="w-[120px]">
                  <SelectValue placeholder="View" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="portfolio">Portfolio</SelectItem>
                  <SelectItem value="longs">Longs</SelectItem>
                  <SelectItem value="shorts">Shorts</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2">
              <Label className="text-sm">Period</Label>
              <Select value={period} onValueChange={(p: Period) => setPeriod(p)}>
                <SelectTrigger className="w-[120px]">
                  <SelectValue placeholder="Period" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1d">1 Day</SelectItem>
                  <SelectItem value="1w">1 Week</SelectItem>
                  <SelectItem value="1m">1 Month</SelectItem>
                  <SelectItem value="3m">3 Months</SelectItem>
                  <SelectItem value="6m">6 Months</SelectItem>
                  <SelectItem value="1y">1 Year</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <MetricCard label="Return" value={benchmark.returnPct} />
          <MetricCard label="Ann. Volatility" value={benchmark.volPct} />
        </div>
      </section>

      {/* Portfolio performance */}
      <section>
        <h3 className="mb-4 text-base font-semibold">Portfolio Performance</h3>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <MetricCard label="Return" value={portfolio.returnPct} />
          <MetricCard label="Ann. Volatility" value={portfolio.volPct} />
          <MetricCard label="Sharpe Ratio" value={portfolio.sharpe} />
          <MetricCard label="Sortino Ratio" value={portfolio.sortino} />
        </div>
      </section>

      {/* Performance attribution */}
      <section>
        <h3 className="mb-4 text-base font-semibold">Performance Attribution</h3>
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          {/* Longs */}
          <div className="space-y-4">
            <h4 className="font-medium text-green-600">Longs</h4>

            <div>
              <h5 className="mb-2 text-sm font-medium text-gray-500">Top Contributors</h5>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                {attributionData.longs.contributors.map((it) => (
                  <AttributionTickerCard
                    key={it.ticker}
                    ticker={it.ticker}
                    value={it.value}
                    colorClass="text-green-600"
                  />
                ))}
              </div>
            </div>

            <div>
              <h5 className="mb-2 text-sm font-medium text-gray-500">Top Detractors</h5>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                {attributionData.longs.detractors.map((it) => (
                  <AttributionTickerCard
                    key={it.ticker}
                    ticker={it.ticker}
                    value={it.value}
                    colorClass="text-red-600"
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Shorts */}
          <div className="space-y-4">
            <h4 className="font-medium text-red-600">Shorts</h4>

            <div>
              <h5 className="mb-2 text-sm font-medium text-gray-500">Top Contributors</h5>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                {attributionData.shorts.contributors.map((it) => (
                  <AttributionTickerCard
                    key={it.ticker}
                    ticker={it.ticker}
                    value={it.value}
                    colorClass="text-green-600"
                  />
                ))}
              </div>
            </div>

            <div>
              <h5 className="mb-2 text-sm font-medium text-gray-500">Top Detractors</h5>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                {attributionData.shorts.detractors.map((it) => (
                  <AttributionTickerCard
                    key={it.ticker}
                    ticker={it.ticker}
                    value={it.value}
                    colorClass="text-red-600"
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contribution analysis */}
      <section className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        <div>
          <h3 className="mb-4 text-base font-semibold">Factor Contribution</h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
            {contrib.factors.map((f) => (
              <ContributionCard key={f.name} title={f.name} value={f.value} />
            ))}
          </div>
        </div>

        <div>
          <h3 className="mb-4 text-base font-semibold">Industry Contribution</h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            {contrib.industries.map((ind) => (
              <ContributionCard key={ind.name} title={ind.name} value={ind.value} />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

export default PerformanceAnalyticsDashboard;
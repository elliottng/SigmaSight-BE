import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const portfolioId = params.id;
    
    // Call existing backend endpoint
    const backendResponse = await fetch(
      `${BACKEND_URL}/api/v1/reports/portfolio/${portfolioId}/content/json`
    );
    
    if (!backendResponse.ok) {
      throw new Error(`Backend API error: ${backendResponse.status}`);
    }
    
    const reportData = await backendResponse.json();
    
    // Transform backend report format to frontend contract
    const summaryData = {
      portfolioId: reportData.portfolio_id || portfolioId,
      name: reportData.portfolio_name || 'Portfolio',
      equity: reportData.content_json?.portfolio_metrics?.total_value || 0,
      grossExposurePct: reportData.content_json?.portfolio_metrics?.gross_exposure_pct || 0,
      netExposurePct: reportData.content_json?.portfolio_metrics?.net_exposure_pct || 0,
      dailyPnl: reportData.content_json?.portfolio_metrics?.daily_pnl || 0,
      dailyReturn: reportData.content_json?.portfolio_metrics?.daily_return || 0,
      positionCount: reportData.content_json?.positions?.length || 0,
      lastUpdated: reportData.generated_date || new Date().toISOString(),
    };
    
    return NextResponse.json(summaryData);
  } catch (error) {
    console.error('Portfolio summary API error:', error);
    return NextResponse.json(
      { 
        error: error instanceof Error ? error.message : 'Failed to fetch portfolio summary',
        portfolioId: params.id
      },
      { status: 500 }
    );
  }
}
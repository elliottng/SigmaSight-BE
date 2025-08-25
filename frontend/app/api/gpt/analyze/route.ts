import { NextRequest, NextResponse } from 'next/server';

const GPT_AGENT_URL = process.env.GPT_AGENT_URL || 'http://localhost:8787';

interface GPTAnalysisRequest {
  portfolio_id: string;
  user_context?: {
    prompt?: string;
    selected_positions?: string[];
    date_range?: { from: Date; to: Date };
    page_context?: string;
  };
  portfolio_report?: any;
}

export async function POST(request: NextRequest) {
  try {
    const body: GPTAnalysisRequest = await request.json();
    const authHeader = request.headers.get('authorization');

    // Forward the request to GPT agent with JWT token passthrough
    const response = await fetch(`${GPT_AGENT_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(authHeader && { 'Authorization': authHeader }),
      },
      body: JSON.stringify({
        portfolio_report: { 
          portfolio_id: body.portfolio_id,
          ...(body.portfolio_report || {})
        },
        user_context: body.user_context?.prompt || 'Provide a comprehensive portfolio analysis',
        context: {
          selected_positions: body.user_context?.selected_positions,
          date_range: body.user_context?.date_range,
          page_context: body.user_context?.page_context,
        }
      }),
    });

    if (!response.ok) {
      throw new Error(`GPT Agent analysis failed: ${response.status} ${response.statusText}`);
    }

    const analysis = await response.json();
    return NextResponse.json(analysis);
  } catch (error) {
    console.error('GPT Agent analysis error:', error);
    return NextResponse.json(
      { 
        success: false,
        error: error instanceof Error ? error.message : 'Analysis failed',
        gaps: ['gpt_agent_unavailable'],
        details: 'Unable to connect to GPT analysis service'
      },
      { status: 500 }
    );
  }
}

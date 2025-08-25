import { NextRequest, NextResponse } from 'next/server';

const GPT_AGENT_URL = process.env.GPT_AGENT_URL || 'http://localhost:8787';

export async function GET() {
  try {
    const response = await fetch(`${GPT_AGENT_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`GPT Agent health check failed: ${response.status}`);
    }

    const healthData = await response.json();
    return NextResponse.json(healthData);
  } catch (error) {
    console.error('GPT Agent health check error:', error);
    return NextResponse.json(
      { 
        status: 'error', 
        backend_connected: false, 
        error: error instanceof Error ? error.message : 'Health check failed' 
      },
      { status: 503 }
    );
  }
}
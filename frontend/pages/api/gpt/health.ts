import type { NextApiRequest, NextApiResponse } from 'next';

interface HealthResponse {
  status: 'ok' | 'error';
  service: string;
  mode: 'direct' | 'agent';
  backend_connected?: boolean;
  backend_url?: string;
  openai_configured?: boolean;
  timestamp: string;
}

export default async function handler(req: NextApiRequest, res: NextApiResponse<HealthResponse>) {
  if (req.method === 'HEAD') {
    // Simple head request for health check
    return res.status(200).end();
  }

  if (req.method !== 'GET') {
    return res.status(405).json({
      status: 'error',
      service: 'sigmasight-gpt-direct',
      mode: 'direct',
      timestamp: new Date().toISOString(),
    } as HealthResponse);
  }

  try {
    // Check OpenAI API key configuration
    const openaiConfigured = !!process.env.OPENAI_API_KEY;
    
    // Check backend connectivity
    let backendConnected = false;
    let backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    
    try {
      const backendResponse = await fetch(`${backendUrl}/api/v1/reports/portfolios`, {
        method: 'HEAD',
        // Add a timeout to prevent hanging
        signal: AbortSignal.timeout(5000),
      });
      backendConnected = backendResponse.ok;
    } catch (error) {
      console.log('Backend health check failed:', error);
      backendConnected = false;
    }

    const healthResponse: HealthResponse = {
      status: 'ok',
      service: 'sigmasight-gpt-direct',
      mode: 'direct',
      backend_connected: backendConnected,
      backend_url: backendUrl,
      openai_configured: openaiConfigured,
      timestamp: new Date().toISOString(),
    };

    return res.status(200).json(healthResponse);
  } catch (error) {
    console.error('Health check error:', error);
    
    return res.status(500).json({
      status: 'error',
      service: 'sigmasight-gpt-direct',
      mode: 'direct',
      timestamp: new Date().toISOString(),
    });
  }
}
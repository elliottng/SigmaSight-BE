import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string; format: string } }
) {
  try {
    const { id, format } = params;
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    
    // Forward the request to the backend
    const response = await fetch(`${backendUrl}/api/v1/reports/portfolio/${id}/content/${format}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // Forward authorization header if present
        ...(request.headers.get('authorization') && {
          'authorization': request.headers.get('authorization')!
        })
      }
    });

    if (!response.ok) {
      console.error(`Backend API error: ${response.status} ${response.statusText}`);
      return NextResponse.json(
        { error: 'Failed to fetch report content from backend' },
        { status: response.status }
      );
    }

    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching report content:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

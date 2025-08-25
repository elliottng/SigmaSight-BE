import type { NextApiRequest, NextApiResponse } from 'next';

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    full_name: string;
    is_active: boolean;
    created_at: string;
  };
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ detail: 'Method not allowed' });
  }

  try {
    const { email, password }: LoginRequest = req.body;

    if (!email || !password) {
      return res.status(422).json({ 
        detail: 'Email and password are required' 
      });
    }

    // Try to authenticate with backend
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    
    try {
      const response = await fetch(`${backendUrl}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
        // Add timeout to prevent hanging
        signal: AbortSignal.timeout(10000),
      });

      if (response.ok) {
        const data: LoginResponse = await response.json();
        return res.status(200).json(data);
      } else {
        const errorData = await response.json();
        console.log('Backend auth failed:', response.status, errorData);
        
        // Fall through to demo mode
      }
    } catch (backendError) {
      console.log('Backend auth error:', backendError);
      // Fall through to demo mode
    }

    // Demo mode authentication (fallback)
    const demoUsers = [
      {
        email: 'demo_individual@sigmasight.com',
        id: 'a3209353-9ed5-4885-81e8-d4bbc995f96c',
        full_name: 'Demo Individual Investor',
        portfolioId: 'a3209353-9ed5-4885-81e8-d4bbc995f96c'
      },
      {
        email: 'demo_hnw@sigmasight.com',
        id: '14e7f420-b096-4e2e-8cc2-531caf434c05',
        full_name: 'Demo High Net Worth Investor',
        portfolioId: '14e7f420-b096-4e2e-8cc2-531caf434c05'
      },
      {
        email: 'demo_hedgefundstyle@sigmasight.com',
        id: 'cf890da7-7b74-4cb4-acba-2205fdd9dff4',
        full_name: 'Demo Hedge Fund Manager',
        portfolioId: 'cf890da7-7b74-4cb4-acba-2205fdd9dff4'
      }
    ];

    const demoUser = demoUsers.find(user => user.email === email);
    
    if (!demoUser) {
      return res.status(401).json({ 
        detail: 'Invalid email. Use one of the demo accounts.' 
      });
    }

    if (password !== 'demo12345') {
      return res.status(401).json({ 
        detail: 'Invalid password. Use "demo12345" for demo accounts.' 
      });
    }

    // Return demo authentication response
    const demoResponse: LoginResponse = {
      access_token: `demo_token_${demoUser.id}_${Date.now()}`,
      token_type: 'bearer',
      user: {
        id: demoUser.id,
        email: demoUser.email,
        full_name: demoUser.full_name,
        is_active: true,
        created_at: new Date().toISOString(),
      }
    };

    return res.status(200).json(demoResponse);

  } catch (error) {
    console.error('Login API error:', error);
    return res.status(500).json({ 
      detail: 'Internal server error' 
    });
  }
}
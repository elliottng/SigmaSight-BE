import Link from 'next/link';
import { useState, useEffect } from 'react';

const DEMO_PORTFOLIOS = [
  { 
    id: 'a3209353-9ed5-4885-81e8-d4bbc995f96c', 
    name: 'Demo Individual Portfolio',
    description: 'Individual investor portfolio with diversified holdings'
  },
  { 
    id: '14e7f420-b096-4e2e-8cc2-531caf434c05', 
    name: 'Demo High Net Worth Portfolio',
    description: 'High net worth portfolio with advanced strategies'
  },
  { 
    id: 'cf890da7-7b74-4cb4-acba-2205fdd9dff4', 
    name: 'Demo Hedge Fund Portfolio',
    description: 'Institutional hedge fund-style portfolio'
  },
];

export default function HomePage() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');

  useEffect(() => {
    // Check backend connectivity with health endpoint
    Promise.race([
      fetch('http://localhost:8000/health').then(response => response.ok),
      new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 3000))
    ])
      .then((isHealthy) => {
        if (isHealthy) {
          // Double-check with portfolios endpoint
          return fetch('http://localhost:8000/api/v1/reports/portfolios')
            .then(response => response.ok);
        }
        return false;
      })
      .then(isConnected => setBackendStatus(isConnected ? 'connected' : 'disconnected'))
      .catch(() => setBackendStatus('disconnected'));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">SigmaSight</h1>
              <p className="text-gray-500">Portfolio Risk Management Platform</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                backendStatus === 'connected' ? 'bg-green-500' : 
                backendStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'
              }`}></div>
              <span className="text-sm text-gray-600">
                Backend {backendStatus === 'connected' ? 'Connected' : 
                        backendStatus === 'disconnected' ? 'Disconnected' : 'Checking...'}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Main Actions */}
        <div className="text-center mb-12">
          <div className="flex justify-center space-x-4">
            <Link href="/login" className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-colors shadow-lg">
              👤 Login to Your Portfolio
            </Link>
            <Link href="/chat" className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors">
              💬 General Chat (No Login)
            </Link>
          </div>
        </div>

        {/* Demo User Profiles - Login Required */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Demo User Profiles</h2>
          <p className="text-center text-gray-600 mb-8">Choose an investor profile to explore their personalized portfolio dashboard</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {DEMO_PORTFOLIOS.map((portfolio) => (
              <div key={portfolio.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border border-gray-200">
                <div className="flex items-center mb-3">
                  <div className="bg-blue-100 rounded-full p-2 mr-3">
                    <span className="text-blue-600">👤</span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">{portfolio.name}</h3>
                </div>
                
                <p className="text-gray-600 mb-4">{portfolio.description}</p>
                
                <div className="bg-gray-50 rounded-lg p-3 mb-4">
                  <div className="text-sm font-medium text-gray-700 mb-1">Login Required</div>
                  <div className="text-xs text-gray-500">Access this user's complete portfolio analytics</div>
                </div>
                
                <Link 
                  href="/login" 
                  className="inline-flex items-center justify-center w-full px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                >
                  🔐 Login as {portfolio.name.replace('Demo ', '')}
                </Link>
              </div>
            ))}
          </div>
          
          <div className="text-center mt-6">
            <p className="text-sm text-gray-600">
              All demo accounts use password: <code className="bg-gray-100 px-2 py-1 rounded">demo12345</code>
            </p>
          </div>
        </div>

        {/* Feature Overview */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full p-3 w-12 h-12 flex items-center justify-center mx-auto mb-4">
              <span className="text-blue-600 text-xl">📊</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Portfolio Analysis</h3>
            <p className="text-gray-600 text-sm">
              Comprehensive portfolio analytics with real-time data, factor exposures, and risk metrics.
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-green-100 rounded-full p-3 w-12 h-12 flex items-center justify-center mx-auto mb-4">
              <span className="text-green-600 text-xl">🤖</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Insights</h3>
            <p className="text-gray-600 text-sm">
              Get intelligent analysis and actionable recommendations powered by advanced language models.
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-purple-100 rounded-full p-3 w-12 h-12 flex items-center justify-center mx-auto mb-4">
              <span className="text-purple-600 text-xl">⚡</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Real-Time Risk</h3>
            <p className="text-gray-600 text-sm">
              Advanced risk management with VaR calculations, stress testing, and correlation analysis.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
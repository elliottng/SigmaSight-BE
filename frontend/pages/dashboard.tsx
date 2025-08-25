import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [portfolioId, setPortfolioId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in
    const storedUser = localStorage.getItem('user');
    const storedPortfolioId = localStorage.getItem('portfolioId');
    
    if (storedUser && storedPortfolioId) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
        setPortfolioId(storedPortfolioId);
      } catch (error) {
        console.error('Error parsing user data:', error);
        router.push('/login');
      }
    } else {
      router.push('/login');
    }
    
    setIsLoading(false);
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    localStorage.removeItem('portfolioId');
    localStorage.removeItem('demo_mode');
    router.push('/');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!user || !portfolioId) {
    return null; // Will redirect to login
  }

  const getUserTypeFromEmail = (email: string) => {
    if (email.includes('individual')) return 'Individual Investor';
    if (email.includes('hnw')) return 'High Net Worth Investor';
    if (email.includes('hedgefundstyle')) return 'Hedge Fund Manager';
    return 'Investor';
  };

  const getPortfolioDescription = (email: string) => {
    if (email.includes('individual')) 
      return 'Diversified portfolio with ETFs and individual stocks focusing on long-term growth';
    if (email.includes('hnw')) 
      return 'Advanced strategies including options, alternatives, and sophisticated risk management';
    if (email.includes('hedgefundstyle')) 
      return 'Complex institutional portfolio with long/short positions and derivative strategies';
    return 'Portfolio with various investment strategies';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">SigmaSight Dashboard</h1>
              <p className="text-gray-500">Welcome back, {user.full_name}</p>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right text-sm">
                <div className="font-medium text-gray-900">{getUserTypeFromEmail(user.email)}</div>
                <div className="text-gray-500">{user.email}</div>
              </div>
              <button 
                onClick={handleLogout}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* User Portfolio Overview */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Portfolio</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Portfolio Overview</h3>
              <p className="text-gray-600 mb-4">{getPortfolioDescription(user.email)}</p>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-1">Portfolio ID</div>
                <div className="font-mono text-sm text-gray-800">{portfolioId}</div>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center">
                  <span className="text-blue-600 text-2xl mr-3">📊</span>
                  <div>
                    <div className="font-semibold text-blue-900">Portfolio Analytics</div>
                    <div className="text-sm text-blue-700">Risk metrics, factor exposures, performance attribution</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center">
                  <span className="text-green-600 text-2xl mr-3">🤖</span>
                  <div>
                    <div className="font-semibold text-green-900">AI-Powered Analysis</div>
                    <div className="text-sm text-green-700">Get intelligent insights and recommendations</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Portfolio Dashboard */}
          <Link 
            href={`/portfolio/${portfolioId}`}
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow group"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="bg-blue-100 rounded-full p-3">
                <span className="text-blue-600 text-2xl">📈</span>
              </div>
              <span className="text-gray-400 group-hover:text-gray-600">→</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Portfolio Dashboard</h3>
            <p className="text-gray-600 text-sm">
              View comprehensive portfolio analytics including risk metrics, factor exposures, and performance data.
            </p>
          </Link>

          {/* AI Chat */}
          <Link 
            href={`/chat?portfolio=${portfolioId}`}
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow group"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="bg-green-100 rounded-full p-3">
                <span className="text-green-600 text-2xl">💬</span>
              </div>
              <span className="text-gray-400 group-hover:text-gray-600">→</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">AI Portfolio Assistant</h3>
            <p className="text-gray-600 text-sm">
              Chat with AI about your portfolio performance, risk analysis, and get personalized insights.
            </p>
          </Link>

          {/* Risk Analysis */}
          <div className="bg-white rounded-lg shadow p-6 opacity-60">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-purple-100 rounded-full p-3">
                <span className="text-purple-600 text-2xl">⚡</span>
              </div>
              <span className="text-gray-300">→</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-500 mb-2">Advanced Risk Analytics</h3>
            <p className="text-gray-400 text-sm">
              Deep dive into VaR calculations, stress testing, and scenario analysis. (Coming Soon)
            </p>
          </div>

          {/* Portfolio Modeling */}
          <div className="bg-white rounded-lg shadow p-6 opacity-60">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-orange-100 rounded-full p-3">
                <span className="text-orange-600 text-2xl">🎯</span>
              </div>
              <span className="text-gray-300">→</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-500 mb-2">What-If Modeling</h3>
            <p className="text-gray-400 text-sm">
              Model potential trades and their impact on your portfolio risk and returns. (Coming Soon)
            </p>
          </div>

          {/* Reports */}
          <div className="bg-white rounded-lg shadow p-6 opacity-60">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-indigo-100 rounded-full p-3">
                <span className="text-indigo-600 text-2xl">📋</span>
              </div>
              <span className="text-gray-300">→</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-500 mb-2">Custom Reports</h3>
            <p className="text-gray-400 text-sm">
              Generate and export detailed portfolio reports in multiple formats. (Coming Soon)
            </p>
          </div>

          {/* Settings */}
          <div className="bg-white rounded-lg shadow p-6 opacity-60">
            <div className="flex items-center justify-between mb-4">
              <div className="bg-gray-100 rounded-full p-3">
                <span className="text-gray-600 text-2xl">⚙️</span>
              </div>
              <span className="text-gray-300">→</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-500 mb-2">Settings & Preferences</h3>
            <p className="text-gray-400 text-sm">
              Customize your dashboard, notifications, and analysis preferences. (Coming Soon)
            </p>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Access</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center py-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">Live</div>
              <div className="text-sm text-gray-600">Market Data</div>
            </div>
            <div className="text-center py-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">Real-time</div>
              <div className="text-sm text-gray-600">Risk Monitoring</div>
            </div>
            <div className="text-center py-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">AI-Powered</div>
              <div className="text-sm text-gray-600">Insights</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
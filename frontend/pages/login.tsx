import { useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

const DEMO_USERS = [
  {
    email: 'demo_individual@sigmasight.com',
    name: 'Demo Individual Investor',
    description: 'Individual investor with diversified portfolio',
    portfolioId: 'a3209353-9ed5-4885-81e8-d4bbc995f96c'
  },
  {
    email: 'demo_hnw@sigmasight.com', 
    name: 'Demo High Net Worth Investor',
    description: 'High net worth investor with advanced strategies',
    portfolioId: '14e7f420-b096-4e2e-8cc2-531caf434c05'
  },
  {
    email: 'demo_hedgefundstyle@sigmasight.com',
    name: 'Demo Hedge Fund Manager', 
    description: 'Institutional hedge fund-style portfolio',
    portfolioId: 'cf890da7-7b74-4cb4-acba-2205fdd9dff4'
  }
];

export default function LoginPage() {
  const router = useRouter();
  const [selectedUser, setSelectedUser] = useState<string>('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedUser) {
      setError('Please select a demo user');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: selectedUser,
          password: password || 'demo12345',
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Store the token and user info
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Find the portfolio ID for this user
        const user = DEMO_USERS.find(u => u.email === selectedUser);
        if (user) {
          localStorage.setItem('portfolioId', user.portfolioId);
        }

        // Redirect to dashboard
        router.push('/dashboard');
      } else {
        setError(data.detail || 'Login failed');
      }
    } catch (err) {
      console.error('Login error:', err);
      
      // For now, simulate successful login since backend auth might not be fully set up
      const user = DEMO_USERS.find(u => u.email === selectedUser);
      if (user) {
        localStorage.setItem('user', JSON.stringify({
          email: user.email,
          full_name: user.name,
          id: user.portfolioId,
        }));
        localStorage.setItem('portfolioId', user.portfolioId);
        localStorage.setItem('demo_mode', 'true');
        
        router.push('/dashboard');
      } else {
        setError('Login failed - please try again');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">SigmaSight</h2>
          <p className="mt-2 text-sm text-gray-600">Portfolio Risk Management Platform</p>
        </div>
        <h2 className="mt-6 text-center text-2xl font-bold text-gray-900">
          Choose Demo User
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Select a demo investor profile to explore their portfolio
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form className="space-y-6" onSubmit={handleLogin}>
            {/* Demo User Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Demo User Profile
              </label>
              <div className="mt-2 space-y-3">
                {DEMO_USERS.map((user) => (
                  <div key={user.email} className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        id={user.email}
                        name="user"
                        type="radio"
                        value={user.email}
                        checked={selectedUser === user.email}
                        onChange={(e) => setSelectedUser(e.target.value)}
                        className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300"
                      />
                    </div>
                    <div className="ml-3 text-sm">
                      <label htmlFor={user.email} className="font-medium text-gray-700 cursor-pointer">
                        {user.name}
                      </label>
                      <p className="text-gray-500">{user.description}</p>
                      <p className="text-xs text-gray-400 mt-1">{user.email}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="demo12345 (default)"
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
              </div>
              <p className="mt-1 text-xs text-gray-500">
                Leave blank to use default password: demo12345
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <div className="text-sm text-red-800">
                  {error}
                </div>
              </div>
            )}

            {/* Login Button */}
            <div>
              <button
                type="submit"
                disabled={!selectedUser || isLoading}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Signing in...' : 'Access Demo Portfolio'}
              </button>
            </div>

            <div className="text-center">
              <Link href="/" className="text-sm text-blue-600 hover:text-blue-800">
                ← Back to Homepage
              </Link>
            </div>
          </form>
        </div>
      </div>

      {/* Info Panel */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-2xl">
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-blue-400 text-xl">ℹ️</span>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">
                Demo Mode Information
              </h3>
              <div className="mt-2 text-sm text-blue-700">
                <p>Each demo user has a unique portfolio with different investment strategies:</p>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li><strong>Individual Investor:</strong> Balanced portfolio with ETFs and individual stocks</li>
                  <li><strong>High Net Worth:</strong> Advanced strategies including options and alternatives</li>
                  <li><strong>Hedge Fund Style:</strong> Complex portfolio with long/short positions</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
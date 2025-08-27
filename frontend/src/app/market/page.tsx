'use client'

import { useState, useEffect } from 'react'
import ProtectedRoute from '../../components/auth/ProtectedRoute'
import DashboardLayout from '../../components/layout/DashboardLayout'
import QuoteTable from '../../components/market/QuoteTable'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { positionsApi } from '../../services/api'
import { TrendingUp, BarChart3, Clock, RefreshCcw } from 'lucide-react'
import type { Position } from '../../lib/types'

export default function MarketPage() {
  const [portfolioSymbols, setPortfolioSymbols] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [activeView, setActiveView] = useState<'watchlist' | 'portfolio' | 'indices'>('indices')

  // Predefined symbol lists
  const indices = ['SPY', 'QQQ', 'IWM', 'DIA', 'VTI', 'VEA', 'VWO', 'AGG', 'GLD', 'TLT']
  const watchlist = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK.B', 'JPM', 'JNJ']

  useEffect(() => {
    const fetchPortfolioSymbols = async () => {
      try {
        const positionsData = await positionsApi.getPositions()
        const symbols = [...new Set(positionsData.positions.map(p => p.ticker))]
        setPortfolioSymbols(symbols)
      } catch (error) {
        console.error('Failed to fetch portfolio symbols:', error)
      } finally {
        setLoading(false)
      }
    }

    if (activeView === 'portfolio') {
      fetchPortfolioSymbols()
    } else {
      setLoading(false)
    }
  }, [activeView])

  const getSymbolsForView = () => {
    switch (activeView) {
      case 'portfolio':
        return portfolioSymbols
      case 'watchlist':
        return watchlist
      case 'indices':
      default:
        return indices
    }
  }

  const views = [
    { id: 'indices', label: 'Market Indices', icon: BarChart3, description: 'Major market ETFs and indices' },
    { id: 'portfolio', label: 'Portfolio Holdings', icon: TrendingUp, description: 'Your current positions' },
    { id: 'watchlist', label: 'Watchlist', icon: Clock, description: 'Popular stocks to monitor' },
  ] as const

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-8">
          {/* Page Header */}
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Market Data</h1>
            <p className="text-gray-600 mt-1">
              Real-time quotes and market information
            </p>
          </div>

          {/* View Selector */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {views.map((view) => (
              <Card
                key={view.id}
                className={`cursor-pointer transition-all hover:shadow-md ${
                  activeView === view.id 
                    ? 'ring-2 ring-blue-500 bg-blue-50' 
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => setActiveView(view.id)}
              >
                <CardContent className="pt-6">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${
                      activeView === view.id 
                        ? 'bg-blue-100 text-blue-600' 
                        : 'bg-gray-100 text-gray-600'
                    }`}>
                      <view.icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{view.label}</h3>
                      <p className="text-sm text-gray-600">{view.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Market Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Market Status</p>
                    <p className="text-lg font-semibold text-green-600">Open</p>
                  </div>
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div>
                  <p className="text-sm font-medium text-gray-600">Trading Session</p>
                  <p className="text-lg font-semibold text-gray-900">Regular Hours</p>
                  <p className="text-xs text-gray-500 mt-1">9:30 AM - 4:00 PM ET</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div>
                  <p className="text-sm font-medium text-gray-600">Data Provider</p>
                  <p className="text-lg font-semibold text-gray-900">Polygon.io</p>
                  <p className="text-xs text-gray-500 mt-1">Real-time quotes</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div>
                  <p className="text-sm font-medium text-gray-600">Last Updated</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {new Date().toLocaleTimeString()}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Auto-refresh: 30s</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quotes Display */}
          {loading ? (
            <Card>
              <CardHeader>
                <CardTitle>Loading {views.find(v => v.id === activeView)?.label}...</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="animate-pulse space-y-4">
                  {[...Array(8)].map((_, i) => (
                    <div key={i} className="h-12 bg-gray-200 rounded"></div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ) : (
            <QuoteTable
              symbols={getSymbolsForView()}
              autoRefresh={true}
              refreshInterval={30000}
            />
          )}

          {/* Market Information */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Market News & Events</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="border-l-4 border-blue-500 pl-4">
                    <h4 className="font-semibold text-gray-900">Market Hours</h4>
                    <p className="text-sm text-gray-600">
                      Regular trading: 9:30 AM - 4:00 PM ET<br />
                      Pre-market: 4:00 AM - 9:30 AM ET<br />
                      After-hours: 4:00 PM - 8:00 PM ET
                    </p>
                  </div>
                  
                  <div className="border-l-4 border-green-500 pl-4">
                    <h4 className="font-semibold text-gray-900">Data Freshness</h4>
                    <p className="text-sm text-gray-600">
                      All quotes are real-time during market hours.
                      Outside market hours, last traded prices are shown.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={() => window.open('/positions', '_blank')}
                  >
                    <TrendingUp className="h-4 w-4 mr-2" />
                    View Portfolio Positions
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={() => window.open('/risk', '_blank')}
                  >
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Analyze Portfolio Risk
                  </Button>
                  
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={() => window.location.reload()}
                  >
                    <RefreshCcw className="h-4 w-4 mr-2" />
                    Refresh All Data
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Disclaimer */}
          <Card className="bg-yellow-50 border-yellow-200">
            <CardContent className="pt-6">
              <p className="text-sm text-yellow-800">
                <strong>Disclaimer:</strong> Market data is provided for informational purposes only. 
                Real-time quotes may be delayed. Always verify prices with your broker before making trades.
                SigmaSight is not responsible for trading decisions made based on this data.
              </p>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
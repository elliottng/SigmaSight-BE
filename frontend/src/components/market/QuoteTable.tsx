'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import { marketDataApi } from '../../services/api'
import { 
  RefreshCcw, 
  Search, 
  TrendingUp, 
  TrendingDown,
  Minus
} from 'lucide-react'
import { formatCurrency, formatPercentage, getValueColor, cn } from '../../lib/utils'
import type { MarketQuote } from '../../lib/types'

interface QuoteTableProps {
  symbols?: string[]
  autoRefresh?: boolean
  refreshInterval?: number
}

export default function QuoteTable({ 
  symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK.B'],
  autoRefresh = false,
  refreshInterval = 30000 
}: QuoteTableProps) {
  const [quotes, setQuotes] = useState<MarketQuote[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchSymbol, setSearchSymbol] = useState('')
  const [customSymbols, setCustomSymbols] = useState<string[]>([])

  const allSymbols = [...symbols, ...customSymbols]

  const fetchQuotes = async () => {
    if (allSymbols.length === 0) {
      setLoading(false)
      return
    }

    try {
      setError(null)
      const data = await marketDataApi.getQuotes(allSymbols)
      setQuotes(data)
    } catch (err: any) {
      setError(err.message)
      console.error('Failed to fetch quotes:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchQuotes()

    if (autoRefresh) {
      const interval = setInterval(fetchQuotes, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [allSymbols, autoRefresh, refreshInterval])

  const handleAddSymbol = () => {
    const symbol = searchSymbol.trim().toUpperCase()
    if (symbol && !allSymbols.includes(symbol)) {
      setCustomSymbols(prev => [...prev, symbol])
      setSearchSymbol('')
    }
  }

  const handleRemoveSymbol = (symbol: string) => {
    setCustomSymbols(prev => prev.filter(s => s !== symbol))
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAddSymbol()
    }
  }

  const getChangeIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="h-4 w-4" />
    if (change < 0) return <TrendingDown className="h-4 w-4" />
    return <Minus className="h-4 w-4" />
  }

  if (loading && quotes.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Market Quotes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="animate-pulse flex justify-between items-center py-3">
                <div className="flex items-center space-x-3">
                  <div className="h-4 bg-gray-300 rounded w-16"></div>
                  <div className="h-3 bg-gray-300 rounded w-12"></div>
                </div>
                <div className="h-4 bg-gray-300 rounded w-20"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center space-x-2">
            <span>Market Quotes</span>
            {autoRefresh && (
              <div className="flex items-center space-x-1 text-sm text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Live</span>
              </div>
            )}
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchQuotes}
            disabled={loading}
            className="flex items-center"
          >
            <RefreshCcw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Add Symbol Input */}
        <div className="flex space-x-2 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Add symbol (e.g., AAPL)"
                value={searchSymbol}
                onChange={(e) => setSearchSymbol(e.target.value)}
                onKeyPress={handleKeyPress}
                className="pl-10"
              />
            </div>
          </div>
          <Button onClick={handleAddSymbol} disabled={!searchSymbol.trim()}>
            Add
          </Button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-4 text-sm">
            {error}
          </div>
        )}

        {/* Quotes Table */}
        <div className="space-y-2">
          {quotes.map((quote) => (
            <div key={quote.symbol} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
              <div className="flex items-center space-x-3">
                <div>
                  <div className="font-semibold text-gray-900">{quote.symbol}</div>
                  {quote.timestamp && (
                    <div className="text-xs text-gray-500">
                      {new Date(quote.timestamp).toLocaleTimeString()}
                    </div>
                  )}
                </div>
                {customSymbols.includes(quote.symbol) && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveSymbol(quote.symbol)}
                    className="h-6 w-6 p-0 text-gray-400 hover:text-red-600"
                  >
                    ×
                  </Button>
                )}
              </div>

              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <div className="font-mono font-semibold text-gray-900">
                    {formatCurrency(quote.price)}
                  </div>
                  {quote.volume && (
                    <div className="text-xs text-gray-500">
                      Vol: {quote.volume.toLocaleString()}
                    </div>
                  )}
                </div>

                <div className="text-right min-w-[80px]">
                  <div className={cn(
                    'flex items-center justify-end space-x-1 font-mono',
                    getValueColor(quote.change)
                  )}>
                    {getChangeIcon(quote.change)}
                    <span>
                      {quote.change >= 0 ? '+' : ''}
                      {formatCurrency(quote.change)}
                    </span>
                  </div>
                  <div className={cn(
                    'text-sm font-mono',
                    getValueColor(quote.change_percent)
                  )}>
                    {quote.change_percent >= 0 ? '+' : ''}
                    {formatPercentage(quote.change_percent / 100)}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {quotes.length === 0 && !loading && (
            <div className="text-center py-8 text-gray-500">
              {error ? 'Unable to load market data' : 'No quotes available'}
            </div>
          )}
        </div>

        {/* Market Status */}
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-gray-600">Market Status: Open</span>
            </div>
            <div className="text-gray-500">
              Last updated: {new Date().toLocaleTimeString()}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
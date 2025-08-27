'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'
import MetricCard from '../ui/MetricCard'
import { riskApi } from '../../services/api'
import { RefreshCcw, TrendingUp, TrendingDown, Activity, Zap } from 'lucide-react'
import { formatCurrency, cn } from '../../lib/utils'
import type { GreeksResponse } from '../../lib/types'

interface GreeksDisplayProps {
  view?: 'portfolio' | 'longs' | 'shorts'
  onViewChange?: (view: 'portfolio' | 'longs' | 'shorts') => void
}

export default function GreeksDisplay({ view = 'portfolio', onViewChange }: GreeksDisplayProps) {
  const [greeksData, setGreeksData] = useState<GreeksResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchGreeks = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await riskApi.getGreeks({ view, include_after_expiry: true })
      setGreeksData(data)
    } catch (err: any) {
      setError(err.message)
      console.error('Failed to fetch Greeks:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGreeks()
  }, [view])

  const getGreekDescription = (greek: string) => {
    switch (greek) {
      case 'delta':
        return 'Rate of change in option price per $1 move in underlying'
      case 'gamma':
        return 'Rate of change in delta per $1 move in underlying'
      case 'theta':
        return 'Time decay - daily P&L from time passage'
      case 'vega':
        return 'Sensitivity to 1% change in implied volatility'
      case 'rho':
        return 'Sensitivity to 1% change in interest rates'
      default:
        return ''
    }
  }

  const getGreekIcon = (greek: string) => {
    switch (greek) {
      case 'delta':
        return <TrendingUp className="h-4 w-4" />
      case 'gamma':
        return <Activity className="h-4 w-4" />
      case 'theta':
        return <TrendingDown className="h-4 w-4" />
      case 'vega':
        return <Zap className="h-4 w-4" />
      default:
        return null
    }
  }

  const getGreekColor = (greek: string, value: number) => {
    switch (greek) {
      case 'delta':
        return value > 0 ? 'success' : 'danger'
      case 'gamma':
        return Math.abs(value) > 1000 ? 'danger' : 'success'
      case 'theta':
        return value < 0 ? 'danger' : 'success'
      case 'vega':
        return Math.abs(value) > 1000 ? 'warning' : 'success'
      default:
        return 'info'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-300 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-gray-300 rounded mb-2"></div>
                <div className="h-3 bg-gray-300 rounded w-3/4"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (error || !greeksData) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="pt-6">
          <div className="text-center">
            <p className="text-red-800 mb-4">
              {error || 'Failed to load Greeks data'}
            </p>
            <Button onClick={fetchGreeks} variant="outline" size="sm">
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* View Selector */}
      <div className="flex items-center justify-between">
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          {['portfolio', 'longs', 'shorts'].map((viewOption) => (
            <Button
              key={viewOption}
              variant={view === viewOption ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => onViewChange?.(viewOption as any)}
              className="capitalize"
            >
              {viewOption}
            </Button>
          ))}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={fetchGreeks}
          disabled={loading}
          className="flex items-center"
        >
          <RefreshCcw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Current Greeks */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Greeks</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(greeksData.current).map(([greek, value]) => {
            if (greek === 'visual' || typeof value !== 'number') return null
            
            return (
              <MetricCard
                key={greek}
                title={greek.charAt(0).toUpperCase() + greek.slice(1)}
                value={value}
                format="number"
                subtitle={getGreekDescription(greek)}
                icon={getGreekIcon(greek)}
                visual={{
                  status: getGreekColor(greek, value)
                }}
              />
            )
          })}
        </div>
      </div>

      {/* Gamma Warning */}
      {greeksData.current.visual?.gamma_status === 'danger' && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-3">
              <Activity className="h-6 w-6 text-red-600" />
              <div>
                <h4 className="font-semibold text-red-900">High Gamma Risk</h4>
                <p className="text-red-800 text-sm">
                  {greeksData.current.visual.gamma_message}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* After Expiry Analysis */}
      {greeksData.after_expiry && (
        <Card>
          <CardHeader>
            <CardTitle>Post-Expiration Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Greeks After Expiry</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Delta:</span>
                    <span className="font-mono">{greeksData.after_expiry.delta.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Gamma:</span>
                    <span className="font-mono">{greeksData.after_expiry.gamma.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-3">Expected Changes</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Delta Change:</span>
                    <span className={cn(
                      'font-mono',
                      greeksData.after_expiry.changes.delta >= 0 ? 'text-green-600' : 'text-red-600'
                    )}>
                      {greeksData.after_expiry.changes.delta >= 0 ? '+' : ''}
                      {greeksData.after_expiry.changes.delta.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Gamma Reduction:</span>
                    <span className="font-mono text-green-600">
                      {greeksData.after_expiry.changes.gamma.toLocaleString()} 
                      ({greeksData.after_expiry.changes.gamma_percent.toFixed(1)}%)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Greeks Interpretation Guide */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-900">Greeks Interpretation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <h5 className="font-medium text-blue-900 mb-2">Positive Values</h5>
              <ul className="space-y-1 text-blue-800">
                <li><strong>Delta +:</strong> Long exposure to underlying movement</li>
                <li><strong>Gamma +:</strong> Delta increases as underlying rises</li>
                <li><strong>Theta +:</strong> Earning time premium</li>
                <li><strong>Vega +:</strong> Benefiting from volatility increases</li>
              </ul>
            </div>
            <div>
              <h5 className="font-medium text-blue-900 mb-2">Negative Values</h5>
              <ul className="space-y-1 text-blue-800">
                <li><strong>Delta -:</strong> Short exposure to underlying movement</li>
                <li><strong>Gamma -:</strong> Delta decreases as underlying rises</li>
                <li><strong>Theta -:</strong> Losing time premium daily</li>
                <li><strong>Vega -:</strong> Hurt by volatility increases</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
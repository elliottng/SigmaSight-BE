'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'
import { riskApi } from '../../services/api'
import { RefreshCcw, Info, TrendingUp, TrendingDown } from 'lucide-react'
import { formatPercentage, cn } from '../../lib/utils'
import type { FactorExposure, FactorDefinition } from '../../lib/types'

interface FactorExposureProps {
  view?: 'portfolio' | 'longs' | 'shorts'
  onViewChange?: (view: 'portfolio' | 'longs' | 'shorts') => void
}

export default function FactorExposureDisplay({ view = 'portfolio', onViewChange }: FactorExposureProps) {
  const [exposures, setExposures] = useState<FactorExposure[]>([])
  const [definitions, setDefinitions] = useState<FactorDefinition[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [exposuresData, definitionsData] = await Promise.all([
        riskApi.getFactorExposures({ view }),
        riskApi.getFactorDefinitions()
      ])
      setExposures(exposuresData)
      setDefinitions(definitionsData)
    } catch (err: any) {
      setError(err.message)
      console.error('Failed to fetch factor data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [view])

  const getFactorDefinition = (factorName: string) => {
    return definitions.find(def => def.factor_name === factorName)
  }

  const getExposureColor = (exposure: number) => {
    const absExposure = Math.abs(exposure)
    if (absExposure >= 0.5) return 'danger'
    if (absExposure >= 0.3) return 'warning'
    if (absExposure >= 0.1) return 'info'
    return 'success'
  }

  const getExposureDirection = (exposure: number) => {
    if (exposure > 0.05) return 'positive'
    if (exposure < -0.05) return 'negative'
    return 'neutral'
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-300 rounded w-1/4"></div>
          <div className="grid grid-cols-1 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-300 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error || exposures.length === 0) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="pt-6">
          <div className="text-center">
            <p className="text-red-800 mb-4">
              {error || 'No factor exposure data available'}
            </p>
            <Button onClick={fetchData} variant="outline" size="sm">
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
          onClick={fetchData}
          disabled={loading}
          className="flex items-center"
        >
          <RefreshCcw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Factor Exposures */}
      <Card>
        <CardHeader>
          <CardTitle>Factor Exposures</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {exposures.map((factor) => {
              const definition = getFactorDefinition(factor.factor_name)
              const direction = getExposureDirection(factor.exposure)
              
              return (
                <div key={factor.factor_name} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-3">
                      <h4 className="font-semibold text-gray-900">
                        {factor.factor_name}
                      </h4>
                      {definition?.etf_ticker && (
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                          {definition.etf_ticker}
                        </span>
                      )}
                      {definition?.calculation_method === 'mock' && (
                        <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                          Simulated
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      {direction === 'positive' && <TrendingUp className="h-4 w-4 text-green-600" />}
                      {direction === 'negative' && <TrendingDown className="h-4 w-4 text-red-600" />}
                      <span className={cn(
                        'font-mono font-semibold',
                        direction === 'positive' ? 'text-green-600' :
                        direction === 'negative' ? 'text-red-600' :
                        'text-gray-600'
                      )}>
                        {factor.exposure >= 0 ? '+' : ''}{factor.exposure.toFixed(3)}
                      </span>
                    </div>
                  </div>

                  {definition?.description && (
                    <p className="text-sm text-gray-600 mb-3">
                      {definition.description}
                    </p>
                  )}

                  <div className="flex items-center space-x-4">
                    {/* Exposure Bar */}
                    <div className="flex-1">
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                        <span>-1.0</span>
                        <span>0</span>
                        <span>+1.0</span>
                      </div>
                      <div className="relative h-2 bg-gray-200 rounded-full">
                        {/* Zero line */}
                        <div className="absolute left-1/2 top-0 w-0.5 h-2 bg-gray-400 transform -translate-x-0.5"></div>
                        
                        {/* Exposure bar */}
                        <div
                          className={cn(
                            'absolute top-0 h-2 rounded-full',
                            direction === 'positive' ? 'bg-green-500' :
                            direction === 'negative' ? 'bg-red-500' :
                            'bg-gray-400'
                          )}
                          style={{
                            left: factor.exposure >= 0 ? '50%' : `${50 + (factor.exposure * 50)}%`,
                            width: `${Math.abs(factor.exposure) * 50}%`,
                          }}
                        />
                      </div>
                    </div>

                    {/* Visual Indicator */}
                    {factor.exposure_visual?.percentage !== undefined && (
                      <div className="text-right">
                        <div className="text-sm font-medium">
                          {factor.exposure_visual.percentage}%
                        </div>
                        <div className={cn(
                          'text-xs px-2 py-1 rounded',
                          factor.exposure_visual.status === 'success' ? 'bg-green-100 text-green-800' :
                          factor.exposure_visual.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                          factor.exposure_visual.status === 'danger' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        )}>
                          {factor.exposure_visual.status?.toUpperCase()}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Factor Interpretation Guide */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-900 flex items-center">
            <Info className="h-5 w-5 mr-2" />
            Factor Exposure Guide
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div>
              <h5 className="font-medium text-blue-900 mb-2">Interpretation</h5>
              <ul className="space-y-1 text-blue-800">
                <li><strong>+1.0:</strong> Perfect positive correlation with factor</li>
                <li><strong>0.0:</strong> No correlation with factor</li>
                <li><strong>-1.0:</strong> Perfect negative correlation with factor</li>
                <li><strong>|0.3|+:</strong> Significant exposure to monitor</li>
              </ul>
            </div>
            <div>
              <h5 className="font-medium text-blue-900 mb-2">Risk Management</h5>
              <ul className="space-y-1 text-blue-800">
                <li><strong>Diversification:</strong> Spread exposures across factors</li>
                <li><strong>Concentration:</strong> Avoid extreme single-factor bets</li>
                <li><strong>Hedging:</strong> Use opposing factors to reduce risk</li>
                <li><strong>Monitoring:</strong> Track factor performance trends</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {exposures.filter(f => Math.abs(f.exposure) > 0.3).length}
              </div>
              <div className="text-sm text-gray-600">High Exposures</div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {exposures.filter(f => f.exposure > 0.05).length}
              </div>
              <div className="text-sm text-gray-600">Positive Exposures</div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                {Math.max(...exposures.map(f => Math.abs(f.exposure))).toFixed(3)}
              </div>
              <div className="text-sm text-gray-600">Largest Exposure</div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
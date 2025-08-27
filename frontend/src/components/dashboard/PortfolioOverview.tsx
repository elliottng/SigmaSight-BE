'use client'

import { useState, useEffect } from 'react'
import { portfolioApi } from '../../services/api'
import MetricCard from '../ui/MetricCard'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'
import { TrendingUp, TrendingDown, DollarSign, Activity, AlertTriangle } from 'lucide-react'
import type { PortfolioOverview } from '../../lib/types'

export default function PortfolioOverviewSection() {
  const [portfolioData, setPortfolioData] = useState<PortfolioOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPortfolioData = async () => {
      try {
        const data = await portfolioApi.getOverview()
        
        // Transform backend response to expected frontend format
        if (data.portfolios && data.portfolios.length > 0) {
          const portfolio = data.portfolios[0] // Use first portfolio
          
          const transformedData = {
            total_value: portfolio.total_market_value,
            total_pl: 0, // Backend doesn't provide P&L yet
            total_pl_percent: 0, // Backend doesn't provide P&L percentage yet
            exposures: {
              gross: {
                value: portfolio.total_market_value,
                visual: { status: 'neutral' }
              },
              net: {
                value: portfolio.total_market_value,
                visual: { status: 'neutral', percentage: 100 }
              },
              long: {
                value: portfolio.total_market_value,
                visual: { percentage: 100 }
              },
              short: {
                value: 0,
                visual: { percentage: 0 }
              }
            },
            exposure_calculations: {
              delta: {
                long_exposure: portfolio.total_market_value,
                short_exposure: 0,
                gross_exposure: portfolio.total_market_value,
                net_exposure: portfolio.total_market_value
              }
            },
            ai_insights: null // No AI insights from backend yet
          }
          
          setPortfolioData(transformedData)
        }
      } catch (err: any) {
        setError(err.message)
        console.error('Failed to fetch portfolio overview:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchPortfolioData()
  }, [])

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
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
    )
  }

  if (error) {
    return (
      <Card className="border-red-200 bg-red-50">
        <CardContent className="pt-6">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <p className="text-red-800">Failed to load portfolio data: {error}</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!portfolioData) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-gray-600 text-center">No portfolio data available</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Portfolio Value"
          value={portfolioData.total_value}
          format="currency"
          change={portfolioData.total_pl}
          changeFormat="currency"
          icon={<DollarSign className="h-4 w-4" />}
          visual={{ status: portfolioData.total_pl >= 0 ? 'success' : 'danger' }}
        />

        <MetricCard
          title="Total P&L"
          value={portfolioData.total_pl}
          format="currency"
          subtitle={`${(portfolioData.total_pl_percent || 0).toFixed(1)}% return`}
          icon={portfolioData.total_pl >= 0 ? 
            <TrendingUp className="h-4 w-4" /> : 
            <TrendingDown className="h-4 w-4" />
          }
          visual={{ status: portfolioData.total_pl >= 0 ? 'success' : 'danger' }}
        />

        <MetricCard
          title="Gross Exposure"
          value={portfolioData.exposures.gross.value}
          format="currency"
          visual={portfolioData.exposures.gross.visual}
          icon={<Activity className="h-4 w-4" />}
        />

        <MetricCard
          title="Net Exposure"
          value={portfolioData.exposures.net.value}
          format="currency"
          visual={portfolioData.exposures.net.visual}
          icon={<Activity className="h-4 w-4" />}
        />
      </div>

      {/* Exposure Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Exposure Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">Long Positions</span>
                <div className="text-right">
                  <div className="text-lg font-semibold text-green-600">
                    ${portfolioData.exposures.long.value.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-500">
                    {portfolioData.exposures.long.visual.percentage}% of portfolio
                  </div>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">Short Positions</span>
                <div className="text-right">
                  <div className="text-lg font-semibold text-red-600">
                    ${Math.abs(portfolioData.exposures.short.value).toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-500">
                    {portfolioData.exposures.short.visual.percentage}% of portfolio
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Net Exposure</span>
                  <div className="text-right">
                    <div className="text-lg font-semibold">
                      ${portfolioData.exposures.net.value.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-500">
                      {portfolioData.exposures.net.visual.percentage}% of portfolio
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Delta-Adjusted Exposure</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">Long Delta Exposure</span>
                <div className="text-lg font-semibold text-green-600">
                  ${portfolioData.exposure_calculations.delta.long_exposure.toLocaleString()}
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">Short Delta Exposure</span>
                <div className="text-lg font-semibold text-red-600">
                  ${Math.abs(portfolioData.exposure_calculations.delta.short_exposure).toLocaleString()}
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">Gross Delta Exposure</span>
                <div className="text-lg font-semibold">
                  ${portfolioData.exposure_calculations.delta.gross_exposure.toLocaleString()}
                </div>
              </div>

              <div className="pt-2 border-t">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Net Delta Exposure</span>
                  <div className="text-lg font-semibold">
                    ${portfolioData.exposure_calculations.delta.net_exposure.toLocaleString()}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Insights */}
      {portfolioData.ai_insights && (
        <Card>
          <CardHeader>
            <CardTitle>AI Risk Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {portfolioData.ai_insights.primary_risks && 
               portfolioData.ai_insights.primary_risks.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-800 mb-2">Primary Risks</h4>
                  <ul className="space-y-1">
                    {portfolioData.ai_insights.primary_risks.map((risk, index) => (
                      <li key={index} className="flex items-center text-sm text-red-700">
                        <AlertTriangle className="h-3 w-3 mr-2" />
                        {risk.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {portfolioData.ai_insights.opportunities && 
               portfolioData.ai_insights.opportunities.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-800 mb-2">Opportunities</h4>
                  <ul className="space-y-1">
                    {portfolioData.ai_insights.opportunities.map((opportunity, index) => (
                      <li key={index} className="flex items-center text-sm text-green-700">
                        <TrendingUp className="h-3 w-3 mr-2" />
                        {opportunity.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
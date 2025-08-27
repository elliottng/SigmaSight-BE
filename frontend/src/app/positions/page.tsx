'use client'

import { useState, useEffect } from 'react'
import ProtectedRoute from '../../components/auth/ProtectedRoute'
import DashboardLayout from '../../components/layout/DashboardLayout'
import PositionTable from '../../components/positions/PositionTable'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import MetricCard from '../../components/ui/MetricCard'
import { positionsApi } from '../../services/api'
import { 
  Plus, 
  Download, 
  RefreshCcw, 
  TrendingUp, 
  DollarSign,
  Activity,
  AlertTriangle 
} from 'lucide-react'
import type { Position, PositionsResponse } from '../../lib/types'

export default function PositionsPage() {
  const [positionsData, setPositionsData] = useState<PositionsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchPositions = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await positionsApi.getPositions()
      setPositionsData(data)
    } catch (err: any) {
      setError(err.message)
      console.error('Failed to fetch positions:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPositions()
  }, [])

  const handleEditPosition = (position: Position) => {
    // TODO: Implement edit modal
    console.log('Edit position:', position)
  }

  const handleDeletePosition = async (positionId: string) => {
    if (!confirm('Are you sure you want to delete this position?')) {
      return
    }

    try {
      await positionsApi.deletePosition(positionId)
      // Refresh positions after deletion
      await fetchPositions()
    } catch (err: any) {
      alert('Failed to delete position: ' + err.message)
    }
  }

  const handleAddPosition = () => {
    // TODO: Implement add position modal
    console.log('Add position clicked')
  }

  const handleExportPositions = () => {
    // TODO: Implement export functionality
    console.log('Export positions clicked')
  }

  if (loading && !positionsData) {
    return (
      <ProtectedRoute>
        <DashboardLayout>
          <div className="space-y-6">
            <div className="animate-pulse space-y-4">
              <div className="h-8 bg-gray-300 rounded w-1/4"></div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-24 bg-gray-300 rounded"></div>
                ))}
              </div>
              <div className="h-96 bg-gray-300 rounded"></div>
            </div>
          </div>
        </DashboardLayout>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Page Header */}
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Portfolio Positions</h1>
              <p className="text-gray-600 mt-1">
                Manage and analyze all your portfolio positions
              </p>
            </div>
            <div className="flex space-x-3">
              <Button
                variant="outline"
                onClick={fetchPositions}
                disabled={loading}
                className="flex items-center"
              >
                <RefreshCcw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button
                variant="outline"
                onClick={handleExportPositions}
                className="flex items-center"
              >
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Button
                onClick={handleAddPosition}
                className="flex items-center"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Position
              </Button>
            </div>
          </div>

          {/* Error State */}
          {error && (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="pt-6">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-5 w-5 text-red-600" />
                  <p className="text-red-800">Failed to load positions: {error}</p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={fetchPositions}
                    className="ml-auto"
                  >
                    Retry
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Summary Cards */}
          {positionsData && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard
                title="Total Positions"
                value={positionsData.summary?.total_positions || 0}
                format="number"
                icon={<Activity className="h-4 w-4" />}
              />
              <MetricCard
                title="Gross Exposure"
                value={positionsData.summary?.gross_exposure || 0}
                format="currency"
                icon={<TrendingUp className="h-4 w-4" />}
              />
              <MetricCard
                title="Net Exposure"
                value={positionsData.summary?.net_exposure || 0}
                format="currency"
                icon={<DollarSign className="h-4 w-4" />}
                visual={{
                  status: (positionsData.summary?.net_exposure || 0) > 0 ? 'success' : 'danger'
                }}
              />
            </div>
          )}

          {/* Positions Table */}
          <PositionTable
            positions={positionsData?.positions || []}
            loading={loading}
            onEdit={handleEditPosition}
            onDelete={handleDeletePosition}
          />

          {/* Position Analytics */}
          {positionsData && positionsData.positions.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Position Types Breakdown</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {['LONG', 'SHORT', 'LC', 'LP', 'SC', 'SP'].map(type => {
                      const typePositions = positionsData.positions.filter(p => p.type === type)
                      const typeValue = typePositions.reduce((sum, p) => sum + p.value, 0)
                      const percentage = (typeValue / (positionsData.summary?.gross_exposure || 1)) * 100

                      if (typePositions.length === 0) return null

                      return (
                        <div key={type} className="flex justify-between items-center">
                          <div className="flex items-center space-x-2">
                            <div className={`w-3 h-3 rounded-full ${
                              type.startsWith('L') ? 'bg-green-500' : 'bg-red-500'
                            }`}></div>
                            <span className="text-sm font-medium">
                              {type} ({typePositions.length})
                            </span>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-semibold">
                              ${typeValue.toLocaleString()}
                            </div>
                            <div className="text-xs text-gray-500">
                              {percentage.toFixed(1)}%
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Top Performers</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {positionsData.positions
                      .sort((a, b) => b.pnl_percent - a.pnl_percent)
                      .slice(0, 5)
                      .map(position => (
                        <div key={position.id} className="flex justify-between items-center">
                          <div className="flex items-center space-x-2">
                            <span className="font-medium">{position.ticker}</span>
                            <span className="text-xs text-gray-500">{position.type}</span>
                          </div>
                          <div className="text-right">
                            <div className={`text-sm font-semibold ${
                              position.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {position.pnl >= 0 ? '+' : ''}{position.pnl_percent.toFixed(1)}%
                            </div>
                            <div className="text-xs text-gray-500">
                              ${position.pnl.toLocaleString()}
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
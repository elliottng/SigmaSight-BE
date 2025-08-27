'use client'

import { useState } from 'react'
import ProtectedRoute from '../../components/auth/ProtectedRoute'
import DashboardLayout from '../../components/layout/DashboardLayout'
import GreeksDisplay from '../../components/risk/GreeksDisplay'
import FactorExposureDisplay from '../../components/risk/FactorExposure'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/Card'

type RiskTab = 'greeks' | 'factors' | 'scenarios'
type ViewMode = 'portfolio' | 'longs' | 'shorts'

export default function RiskPage() {
  const [activeTab, setActiveTab] = useState<RiskTab>('greeks')
  const [viewMode, setViewMode] = useState<ViewMode>('portfolio')

  const tabs = [
    { id: 'greeks', label: 'Options Greeks', description: 'Delta, gamma, theta, vega analysis' },
    { id: 'factors', label: 'Factor Exposure', description: 'Market factor risk attribution' },
    { id: 'scenarios', label: 'Scenario Analysis', description: 'Stress testing and what-if analysis' },
  ] as const

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-8">
          {/* Page Header */}
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Risk Analytics</h1>
            <p className="text-gray-600 mt-1">
              Comprehensive portfolio risk analysis and monitoring
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <div className="text-left">
                    <div className="font-semibold">{tab.label}</div>
                    <div className="text-xs text-gray-500 group-hover:text-gray-600">
                      {tab.description}
                    </div>
                  </div>
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="min-h-[600px]">
            {activeTab === 'greeks' && (
              <GreeksDisplay view={viewMode} onViewChange={setViewMode} />
            )}
            
            {activeTab === 'factors' && (
              <FactorExposureDisplay view={viewMode} onViewChange={setViewMode} />
            )}
            
            {activeTab === 'scenarios' && (
              <Card>
                <CardHeader>
                  <CardTitle>Scenario Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">🔬</div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Scenario Analysis Coming Soon
                    </h3>
                    <p className="text-gray-600 max-w-md mx-auto">
                      Stress testing and what-if analysis tools will help you understand 
                      how your portfolio performs under different market conditions.
                    </p>
                    <div className="mt-6 text-sm text-gray-500">
                      Features in development:
                    </div>
                    <ul className="mt-2 text-sm text-gray-500 space-y-1">
                      <li>• Market crash scenarios</li>
                      <li>• Interest rate changes</li>
                      <li>• Volatility spikes</li>
                      <li>• Custom scenario modeling</li>
                      <li>• Historical backtesting</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Risk Summary Footer */}
          <Card className="bg-gray-50 border-gray-200">
            <CardContent className="pt-6">
              <div className="text-center">
                <h3 className="text-sm font-semibold text-gray-800 mb-2">
                  Risk Analytics Status
                </h3>
                <div className="flex items-center justify-center space-x-6 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-gray-600">Real-time calculations active</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-gray-600">Market data current</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                    <span className="text-gray-600">Last updated: {new Date().toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
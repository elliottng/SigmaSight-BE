'use client'

import ProtectedRoute from '../../components/auth/ProtectedRoute'
import DashboardLayout from '../../components/layout/DashboardLayout'
import PortfolioOverview from '../../components/dashboard/PortfolioOverview'
import AlertsPanel from '../../components/dashboard/AlertsPanel'

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-8">
          {/* Page Header */}
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Portfolio Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Monitor your portfolio performance and risk metrics
            </p>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Portfolio Overview - Takes up 2/3 of the space */}
            <div className="lg:col-span-2">
              <PortfolioOverview />
            </div>

            {/* Sidebar - Takes up 1/3 of the space */}
            <div className="space-y-6">
              <AlertsPanel />
              
              {/* Quick Actions */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-gray-800">Quick Actions</h3>
                <div className="grid grid-cols-1 gap-2">
                  <a
                    href="/positions"
                    className="p-3 text-sm bg-white border border-gray-200 rounded-md hover:bg-gray-50 transition-colors"
                  >
                    📊 View All Positions
                  </a>
                  <a
                    href="/risk"
                    className="p-3 text-sm bg-white border border-gray-200 rounded-md hover:bg-gray-50 transition-colors"
                  >
                    🛡️ Risk Analytics
                  </a>
                  <a
                    href="/reports"
                    className="p-3 text-sm bg-white border border-gray-200 rounded-md hover:bg-gray-50 transition-colors"
                  >
                    📋 Generate Report
                  </a>
                </div>
              </div>

              {/* Market Status */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-green-800">Market Open</span>
                </div>
                <p className="text-xs text-green-700 mt-1">
                  Real-time data and calculations active
                </p>
              </div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
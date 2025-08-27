'use client'

import { ReactNode, useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import Navigation from './Navigation'
import { alertsApi } from '../../services/api'

interface DashboardLayoutProps {
  children: ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, loading } = useAuth()
  const [alertCount, setAlertCount] = useState(0)

  useEffect(() => {
    const fetchAlerts = async () => {
      if (user) {
        try {
          const alerts = await alertsApi.getAlerts({ priority: 'critical' })
          setAlertCount(alerts.length)
        } catch (error) {
          console.error('Failed to fetch alerts:', error)
        }
      }
    }

    fetchAlerts()
  }, [user])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading SigmaSight...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null // This will be handled by auth redirects
  }

  return (
    <div className="h-screen flex">
      <Navigation alertCount={alertCount} />
      
      {/* Main content */}
      <div className="flex flex-1 flex-col lg:pl-72">
        <main className="flex-1 overflow-y-auto">
          <div className="px-4 py-6 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
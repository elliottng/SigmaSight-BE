'use client'

import { useState, useEffect } from 'react'
import { alertsApi } from '../../services/api'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'
import { 
  AlertTriangle, 
  Clock, 
  X, 
  TrendingDown, 
  Shield, 
  Calendar 
} from 'lucide-react'
import { formatDateTime, cn } from '../../lib/utils'
import type { Alert } from '../../lib/types'

export default function AlertsPanel() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const data = await alertsApi.getAlerts()
        setAlerts(data)
      } catch (err: any) {
        setError(err.message)
        console.error('Failed to fetch alerts:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAlerts()
  }, [])

  const dismissAlert = async (alertId: string) => {
    try {
      await alertsApi.dismissAlert(alertId)
      setAlerts(alerts.filter(alert => alert.id !== alertId))
    } catch (err) {
      console.error('Failed to dismiss alert:', err)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'text-red-700 bg-red-100 border-red-200'
      case 'high':
        return 'text-orange-700 bg-orange-100 border-orange-200'
      case 'medium':
        return 'text-yellow-700 bg-yellow-100 border-yellow-200'
      default:
        return 'text-blue-700 bg-blue-100 border-blue-200'
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'critical':
        return <AlertTriangle className="h-4 w-4" />
      case 'high':
        return <TrendingDown className="h-4 w-4" />
      case 'medium':
        return <Shield className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'expiration_risk':
        return <Calendar className="h-5 w-5" />
      case 'concentration':
        return <TrendingDown className="h-5 w-5" />
      case 'risk_limit':
        return <Shield className="h-5 w-5" />
      default:
        return <AlertTriangle className="h-5 w-5" />
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Risk Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-300 rounded w-1/2"></div>
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
        <CardTitle className="flex items-center justify-between">
          <span>Risk Alerts</span>
          {alerts.length > 0 && (
            <span className="text-sm text-red-600 bg-red-100 px-2 py-1 rounded-full">
              {alerts.length} active
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {error ? (
          <div className="text-center py-4">
            <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-2" />
            <p className="text-sm text-red-700">Failed to load alerts</p>
          </div>
        ) : alerts.length === 0 ? (
          <div className="text-center py-6">
            <Shield className="h-8 w-8 text-green-500 mx-auto mb-2" />
            <p className="text-sm text-gray-600">No active alerts</p>
            <p className="text-xs text-gray-500 mt-1">Your portfolio is within risk limits</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className={cn(
                  'border rounded-lg p-3',
                  getPriorityColor(alert.priority)
                )}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className="mt-0.5">
                      {getAlertIcon(alert.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="text-sm font-semibold truncate">
                          {alert.title}
                        </h4>
                        <span className={cn(
                          'inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium',
                          getPriorityColor(alert.priority)
                        )}>
                          {getPriorityIcon(alert.priority)}
                          <span className="ml-1 capitalize">{alert.priority}</span>
                        </span>
                      </div>
                      <p className="text-xs mb-2">
                        {alert.message}
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs opacity-75">
                          {formatDateTime(alert.triggered_at)}
                        </span>
                        {alert.actions && alert.actions.length > 0 && (
                          <div className="flex space-x-1">
                            {alert.actions.slice(0, 2).map((action, index) => (
                              <span
                                key={index}
                                className="text-xs px-1.5 py-0.5 bg-white bg-opacity-50 rounded"
                              >
                                {action.replace(/_/g, ' ')}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => dismissAlert(alert.id)}
                    className="ml-2 h-6 w-6 p-0 text-current hover:bg-white hover:bg-opacity-20"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
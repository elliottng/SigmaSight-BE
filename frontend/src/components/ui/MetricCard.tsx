import { ReactNode } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './Card'
import { formatCurrency, formatPercentage, getValueColor, cn } from '../../lib/utils'
import type { VisualIndicator } from '../../lib/types'

interface MetricCardProps {
  title: string
  value: number | string
  format?: 'currency' | 'percentage' | 'number' | 'custom'
  subtitle?: string
  change?: number
  changeFormat?: 'percentage' | 'currency'
  visual?: VisualIndicator
  icon?: ReactNode
  className?: string
  onClick?: () => void
}

export default function MetricCard({
  title,
  value,
  format = 'number',
  subtitle,
  change,
  changeFormat = 'percentage',
  visual,
  icon,
  className,
  onClick,
}: MetricCardProps) {
  const formatValue = (val: number | string) => {
    if (typeof val === 'string') return val
    
    switch (format) {
      case 'currency':
        return formatCurrency(val)
      case 'percentage':
        return formatPercentage(val)
      case 'number':
        return val.toLocaleString()
      default:
        return val.toString()
    }
  }

  const formatChange = (val: number) => {
    switch (changeFormat) {
      case 'currency':
        return formatCurrency(val)
      case 'percentage':
        return formatPercentage(val / 100)
      default:
        return val.toString()
    }
  }

  const getStatusStyles = () => {
    if (!visual?.status) return ''
    
    switch (visual.status) {
      case 'success':
        return 'border-l-4 border-green-500 bg-green-50'
      case 'warning':
        return 'border-l-4 border-yellow-500 bg-yellow-50'
      case 'danger':
        return 'border-l-4 border-red-500 bg-red-50'
      case 'info':
        return 'border-l-4 border-blue-500 bg-blue-50'
      default:
        return ''
    }
  }

  return (
    <Card 
      className={cn(
        'hover:shadow-md transition-shadow',
        getStatusStyles(),
        onClick && 'cursor-pointer hover:shadow-lg',
        className
      )}
      onClick={onClick}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-700">
          {title}
        </CardTitle>
        {icon && (
          <div className="text-gray-400">
            {icon}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="text-2xl font-bold text-gray-900">
            {formatValue(value)}
          </div>
          
          {subtitle && (
            <p className="text-sm text-gray-600">
              {subtitle}
            </p>
          )}
          
          <div className="flex items-center justify-between">
            {change !== undefined && (
              <div className={cn('flex items-center text-sm', getValueColor(change))}>
                <span className="mr-1">
                  {change > 0 ? '↗' : change < 0 ? '↘' : '→'}
                </span>
                {change > 0 && '+'}
                {formatChange(change)}
              </div>
            )}
            
            {visual?.percentage !== undefined && (
              <div className="flex items-center">
                <div className="w-16 bg-gray-200 rounded-full h-2 ml-auto">
                  <div 
                    className={cn(
                      'h-2 rounded-full transition-all',
                      visual.status === 'success' ? 'bg-green-500' :
                      visual.status === 'warning' ? 'bg-yellow-500' :
                      visual.status === 'danger' ? 'bg-red-500' :
                      'bg-blue-500'
                    )}
                    style={{ width: `${Math.min(visual.percentage, 100)}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500 ml-2">
                  {visual.percentage}%
                </span>
              </div>
            )}
          </div>

          {visual?.target_range && (
            <div className="text-xs text-gray-500">
              Target: {formatPercentage(visual.target_range[0])} - {formatPercentage(visual.target_range[1])}
            </div>
          )}

          {visual?.limit && (
            <div className="text-xs text-gray-500">
              Limit: {typeof visual.limit === 'number' ? formatPercentage(visual.limit) : visual.limit}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
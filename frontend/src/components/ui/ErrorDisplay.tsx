import { AlertTriangle, RefreshCcw, Info, XCircle, CheckCircle } from 'lucide-react'
import { Button } from './Button'
import { Card, CardContent } from './Card'
import { cn } from '../../lib/utils'

interface ErrorDisplayProps {
  error: string | Error
  onRetry?: () => void
  retryLabel?: string
  className?: string
  variant?: 'error' | 'warning' | 'info' | 'success'
  title?: string
  showIcon?: boolean
}

export default function ErrorDisplay({
  error,
  onRetry,
  retryLabel = 'Try Again',
  className,
  variant = 'error',
  title,
  showIcon = true
}: ErrorDisplayProps) {
  const errorMessage = typeof error === 'string' ? error : error.message

  const variants = {
    error: {
      container: 'border-red-200 bg-red-50',
      icon: <AlertTriangle className="h-5 w-5 text-red-600" />,
      title: 'text-red-900',
      message: 'text-red-800',
      defaultTitle: 'Error'
    },
    warning: {
      container: 'border-yellow-200 bg-yellow-50',
      icon: <AlertTriangle className="h-5 w-5 text-yellow-600" />,
      title: 'text-yellow-900',
      message: 'text-yellow-800',
      defaultTitle: 'Warning'
    },
    info: {
      container: 'border-blue-200 bg-blue-50',
      icon: <Info className="h-5 w-5 text-blue-600" />,
      title: 'text-blue-900',
      message: 'text-blue-800',
      defaultTitle: 'Information'
    },
    success: {
      container: 'border-green-200 bg-green-50',
      icon: <CheckCircle className="h-5 w-5 text-green-600" />,
      title: 'text-green-900',
      message: 'text-green-800',
      defaultTitle: 'Success'
    }
  }

  const config = variants[variant]

  return (
    <Card className={cn(config.container, className)}>
      <CardContent className="pt-6">
        <div className="flex items-start space-x-3">
          {showIcon && config.icon}
          <div className="flex-1">
            {title && (
              <h4 className={cn('font-semibold mb-1', config.title)}>
                {title}
              </h4>
            )}
            <p className={cn('text-sm', config.message)}>
              {errorMessage}
            </p>
            {onRetry && (
              <div className="mt-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onRetry}
                  className="flex items-center"
                >
                  <RefreshCcw className="h-4 w-4 mr-2" />
                  {retryLabel}
                </Button>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Inline error display for smaller spaces
export function InlineErrorDisplay({
  error,
  onRetry,
  retryLabel = 'Retry',
  variant = 'error'
}: ErrorDisplayProps) {
  const errorMessage = typeof error === 'string' ? error : error.message

  const colors = {
    error: 'text-red-700 bg-red-50 border-red-200',
    warning: 'text-yellow-700 bg-yellow-50 border-yellow-200', 
    info: 'text-blue-700 bg-blue-50 border-blue-200',
    success: 'text-green-700 bg-green-50 border-green-200'
  }

  return (
    <div className={cn('border rounded-md p-3 text-sm', colors[variant])}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <XCircle className="h-4 w-4 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
        {onRetry && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onRetry}
            className={cn(
              'h-auto p-1 text-xs hover:bg-white hover:bg-opacity-50',
              variant === 'error' && 'text-red-700 hover:text-red-800',
              variant === 'warning' && 'text-yellow-700 hover:text-yellow-800',
              variant === 'info' && 'text-blue-700 hover:text-blue-800',
              variant === 'success' && 'text-green-700 hover:text-green-800'
            )}
          >
            {retryLabel}
          </Button>
        )}
      </div>
    </div>
  )
}

// Toast-style notification
export function NotificationDisplay({
  error,
  variant = 'error',
  onDismiss,
  autoHide = true,
  duration = 5000
}: ErrorDisplayProps & {
  onDismiss?: () => void
  autoHide?: boolean
  duration?: number
}) {
  const errorMessage = typeof error === 'string' ? error : error.message

  // Auto-hide logic would go here in a real implementation
  // useEffect(() => {
  //   if (autoHide) {
  //     const timer = setTimeout(onDismiss, duration)
  //     return () => clearTimeout(timer)
  //   }
  // }, [autoHide, duration, onDismiss])

  const config = {
    error: 'bg-red-600 text-white',
    warning: 'bg-yellow-600 text-white',
    info: 'bg-blue-600 text-white', 
    success: 'bg-green-600 text-white'
  }

  return (
    <div className={cn('rounded-lg p-4 shadow-lg', config[variant])}>
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">{errorMessage}</p>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="ml-4 text-white hover:text-gray-200 transition-colors"
          >
            <XCircle className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  )
}
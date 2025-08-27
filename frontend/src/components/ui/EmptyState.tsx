import { ReactNode } from 'react'
import { Button } from './Button'
import { Card, CardContent } from './Card'
import { cn } from '../../lib/utils'

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
    variant?: 'primary' | 'secondary' | 'outline'
  }
  secondaryAction?: {
    label: string
    onClick: () => void
  }
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export default function EmptyState({
  icon,
  title,
  description,
  action,
  secondaryAction,
  className,
  size = 'md'
}: EmptyStateProps) {
  const sizes = {
    sm: {
      container: 'py-6',
      icon: 'h-8 w-8',
      title: 'text-lg',
      description: 'text-sm',
      spacing: 'space-y-3'
    },
    md: {
      container: 'py-12',
      icon: 'h-12 w-12',
      title: 'text-xl',
      description: 'text-base',
      spacing: 'space-y-4'
    },
    lg: {
      container: 'py-16',
      icon: 'h-16 w-16',
      title: 'text-2xl',
      description: 'text-lg',
      spacing: 'space-y-6'
    }
  }

  const config = sizes[size]

  return (
    <div className={cn('text-center', config.container, className)}>
      <div className={config.spacing}>
        {icon && (
          <div className={cn('mx-auto text-gray-400', config.icon)}>
            {icon}
          </div>
        )}
        
        <div>
          <h3 className={cn('font-semibold text-gray-900', config.title)}>
            {title}
          </h3>
          {description && (
            <p className={cn('text-gray-600 mt-2', config.description)}>
              {description}
            </p>
          )}
        </div>

        {(action || secondaryAction) && (
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            {action && (
              <Button
                onClick={action.onClick}
                variant={action.variant || 'primary'}
              >
                {action.label}
              </Button>
            )}
            {secondaryAction && (
              <Button
                onClick={secondaryAction.onClick}
                variant="outline"
              >
                {secondaryAction.label}
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// Card wrapper for empty states
export function EmptyStateCard(props: EmptyStateProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <EmptyState {...props} />
      </CardContent>
    </Card>
  )
}

// Common empty state configurations
export const EmptyStates = {
  NoData: (props: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="text-6xl">📊</div>}
      title="No data available"
      description="There's no data to display at the moment."
      {...props}
    />
  ),
  
  NoResults: (props: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="text-6xl">🔍</div>}
      title="No results found"
      description="Try adjusting your search criteria or filters."
      {...props}
    />
  ),
  
  NoPositions: (props: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="text-6xl">📈</div>}
      title="No positions yet"
      description="Add your first position to start tracking your portfolio."
      {...props}
    />
  ),
  
  NoReports: (props: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="text-6xl">📋</div>}
      title="No reports generated"
      description="Generate your first report to see it here."
      {...props}
    />
  ),
  
  ComingSoon: (props: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="text-6xl">🚀</div>}
      title="Coming Soon"
      description="This feature is currently in development."
      {...props}
    />
  ),
  
  Maintenance: (props: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="text-6xl">🔧</div>}
      title="Under Maintenance"
      description="This feature is temporarily unavailable while we make improvements."
      {...props}
    />
  ),
  
  Error: (props: Partial<EmptyStateProps>) => (
    <EmptyState
      icon={<div className="text-6xl">⚠️</div>}
      title="Something went wrong"
      description="We encountered an error loading this content."
      {...props}
    />
  )
}
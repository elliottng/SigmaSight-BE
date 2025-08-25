'use client';

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { cn } from '@/lib/utils';

interface InsightCardProps {
  title: string;
  data: Record<string, any>;
  compact?: boolean;
  className?: string;
}

export function InsightCard({ title, data, compact = false, className }: InsightCardProps) {
  const formatValue = (key: string, value: any): string => {
    if (value === null || value === undefined) return '--';
    
    // Format currency values
    if (key.toLowerCase().includes('value') || key.toLowerCase().includes('pnl')) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        notation: value > 1000000 ? 'compact' : 'standard'
      }).format(value);
    }
    
    // Format percentage values
    if (key.toLowerCase().includes('pct') || key.toLowerCase().includes('percent') || key.toLowerCase().includes('return')) {
      return `${(value * 100).toFixed(2)}%`;
    }
    
    // Format ratios and decimals
    if (typeof value === 'number') {
      if (value < 1 && value > 0) {
        return (value * 100).toFixed(2) + '%';
      }
      return value.toLocaleString();
    }
    
    return String(value);
  };

  const formatKey = (key: string): string => {
    return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (!data || Object.keys(data).length === 0) {
    return (
      <Card className={cn('opacity-50', className)}>
        <CardContent className={compact ? 'p-4' : 'p-6'}>
          <p className="text-sm text-muted-foreground">{title}: No data available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className={compact ? 'pb-2' : 'pb-4'}>
        <CardTitle className={compact ? 'text-sm' : 'text-base'}>{title}</CardTitle>
      </CardHeader>
      <CardContent className={compact ? 'p-4 pt-0' : 'p-6 pt-0'}>
        <div className={cn(
          'grid gap-2',
          compact ? 'grid-cols-1' : 'grid-cols-1 sm:grid-cols-2'
        )}>
          {Object.entries(data).map(([key, value]) => (
            <div key={key} className="flex justify-between items-center">
              <span className={cn(
                'font-medium',
                compact ? 'text-xs' : 'text-sm',
                'text-muted-foreground'
              )}>
                {formatKey(key)}:
              </span>
              <span className={cn(
                'font-semibold',
                compact ? 'text-xs' : 'text-sm',
                'text-foreground'
              )}>
                {formatValue(key, value)}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// Specialized insight cards for different data types
interface FactorCardProps {
  factors: Array<{ name: string; exposure: number; description?: string }>;
  compact?: boolean;
  className?: string;
}

export function FactorCard({ factors, compact = false, className }: FactorCardProps) {
  if (!factors || factors.length === 0) {
    return (
      <Card className={cn('opacity-50', className)}>
        <CardContent className={compact ? 'p-4' : 'p-6'}>
          <p className="text-sm text-muted-foreground">No factor exposures available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader className={compact ? 'pb-2' : 'pb-4'}>
        <CardTitle className={compact ? 'text-sm' : 'text-base'}>Factor Exposures</CardTitle>
      </CardHeader>
      <CardContent className={compact ? 'p-4 pt-0' : 'p-6 pt-0'}>
        <div className="space-y-3">
          {factors.slice(0, compact ? 3 : 5).map((factor, index) => (
            <div key={index} className="space-y-1">
              <div className="flex justify-between items-center">
                <span className={cn(
                  'font-medium',
                  compact ? 'text-xs' : 'text-sm'
                )}>
                  {factor.name}
                </span>
                <span className={cn(
                  'font-semibold',
                  compact ? 'text-xs' : 'text-sm',
                  factor.exposure > 0 ? 'text-green-600' : 'text-red-600'
                )}>
                  {(factor.exposure * 100).toFixed(1)}%
                </span>
              </div>
              
              {/* Visual bar */}
              <div className="w-full bg-muted rounded-full h-1">
                <div
                  className={cn(
                    'h-1 rounded-full transition-all duration-300',
                    factor.exposure > 0 ? 'bg-green-500' : 'bg-red-500'
                  )}
                  style={{
                    width: `${Math.min(Math.abs(factor.exposure) * 100, 100)}%`
                  }}
                />
              </div>
              
              {factor.description && !compact && (
                <p className="text-xs text-muted-foreground">{factor.description}</p>
              )}
            </div>
          ))}
          
          {factors.length > (compact ? 3 : 5) && (
            <p className="text-xs text-muted-foreground text-center">
              +{factors.length - (compact ? 3 : 5)} more factors
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// Action items component
interface ActionItemsProps {
  actions: string[];
  compact?: boolean;
  className?: string;
}

export function ActionItems({ actions, compact = false, className }: ActionItemsProps) {
  if (!actions || actions.length === 0) {
    return null;
  }

  return (
    <Card className={className}>
      <CardHeader className={compact ? 'pb-2' : 'pb-4'}>
        <CardTitle className={compact ? 'text-sm' : 'text-base'}>Recommendations</CardTitle>
      </CardHeader>
      <CardContent className={compact ? 'p-4 pt-0' : 'p-6 pt-0'}>
        <ul className="space-y-2">
          {actions.slice(0, compact ? 3 : actions.length).map((action, index) => (
            <li key={index} className="flex items-start">
              <span className="mr-2 text-blue-500">→</span>
              <span className={cn(
                compact ? 'text-xs' : 'text-sm',
                'text-foreground'
              )}>
                {action}
              </span>
            </li>
          ))}
          
          {compact && actions.length > 3 && (
            <li className="text-xs text-muted-foreground text-center">
              +{actions.length - 3} more recommendations
            </li>
          )}
        </ul>
      </CardContent>
    </Card>
  );
}

// Data gaps alert component
interface GapAlertProps {
  gaps: string[];
  className?: string;
}

export function GapAlert({ gaps, className }: GapAlertProps) {
  if (!gaps || gaps.length === 0) {
    return null;
  }

  return (
    <Card className={cn('border-amber-200 bg-amber-50', className)}>
      <CardContent className="p-4">
        <div className="flex items-start">
          <span className="text-amber-600 mr-2">⚠️</span>
          <div>
            <h4 className="text-sm font-medium text-amber-800 mb-1">Data Gaps Identified</h4>
            <ul className="text-xs text-amber-700 space-y-1">
              {gaps.map((gap, index) => (
                <li key={index}>• {gap.replace(/_/g, ' ')}</li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
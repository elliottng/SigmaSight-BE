'use client';

import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn, formatCurrency, getTrend, getTrendColor } from '@/lib/utils';

interface MetricCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  trend?: 'positive' | 'negative' | 'neutral' | number | string;
  threshold?: number;
  className?: string;
  loading?: boolean;
}

export default function MetricCard({ 
  title, 
  value, 
  subtitle,
  trend, 
  threshold,
  className,
  loading = false
}: MetricCardProps) {
  const numericValue = typeof value === 'string' ? parseFloat(value) : value;
  const trendValue = trend ? (typeof trend === 'number' ? trend : typeof trend === 'string' && !isNaN(parseFloat(trend)) ? parseFloat(trend) : 0) : 0;
  const trendDirection = typeof trend === 'string' && ['positive', 'negative', 'neutral'].includes(trend) ? trend : getTrend(trendValue);
  const trendColorClass = getTrendColor(trendDirection as 'positive' | 'negative' | 'neutral');
  
  if (loading) {
    return (
      <div className={cn(
        "bg-surface border border-border rounded-lg p-4 animate-pulse",
        className
      )}>
        <div className="h-4 bg-border rounded mb-3"></div>
        <div className="h-8 bg-border rounded mb-2"></div>
        <div className="h-3 bg-border rounded w-20"></div>
      </div>
    );
  }
  
  const TrendIcon = trendDirection === 'up' ? TrendingUp : 
                   trendDirection === 'down' ? TrendingDown : 
                   Minus;
  
  return (
    <div className={cn(
      "bg-surface border border-border rounded-lg p-4 hover:border-accent transition-all duration-150",
      "hover:shadow-lg hover:shadow-accent/5",
      className
    )}>
      {/* Title */}
      <h3 className="text-sm text-text-secondary mb-2 font-medium">
        {title}
      </h3>
      
      {/* Value */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl font-bold text-text-primary">
          {typeof numericValue === 'number' ? formatCurrency(numericValue) : value}
        </span>
        
        {trend && (
          <div className={cn(
            "flex items-center gap-1 text-sm font-medium",
            trendColorClass
          )}>
            <TrendIcon className="w-4 h-4" />
            <span>
              {Math.abs(trendValue).toFixed(2)}%
            </span>
          </div>
        )}
      </div>
      
      {/* Progress Bar */}
      {threshold && (
        <div className="w-full bg-border rounded-full h-1.5">
          <div
            className={cn(
              "h-1.5 rounded-full transition-all duration-300",
              numericValue > threshold * 0.8 ? "bg-status-success" :
              numericValue > threshold * 0.6 ? "bg-status-warning" :
              "bg-status-danger"
            )}
            style={{
              width: `${Math.min((numericValue / threshold) * 100, 100)}%`
            }}
          />
        </div>
      )}
    </div>
  );
}
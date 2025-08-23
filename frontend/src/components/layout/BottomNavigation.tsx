'use client';

import React from 'react';
import { Home, Layers, TrendingUp, BarChart3, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';
import { TabKey } from './Layout';

interface BottomNavigationProps {
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
  className?: string;
}

const navigationItems = [
  {
    key: 'dashboard' as TabKey,
    icon: Home,
    label: 'Dashboard',
  },
  {
    key: 'positions' as TabKey,
    icon: Layers,
    label: 'Positions',
  },
  {
    key: 'risk' as TabKey,
    icon: TrendingUp,
    label: 'Risk',
  },
  {
    key: 'performance' as TabKey,
    icon: BarChart3,
    label: 'Performance',
  },
  {
    key: 'reports' as TabKey,
    icon: FileText,
    label: 'Reports',
  },
];

export default function BottomNavigation({ 
  activeTab, 
  onTabChange, 
  className 
}: BottomNavigationProps) {
  return (
    <nav className={cn(
      "fixed bottom-0 left-0 right-0 bg-surface border-t border-border",
      className
    )}>
      <div className="flex justify-around items-center h-16">
        {navigationItems.map(({ key, icon: Icon, label }) => (
          <button
            key={key}
            onClick={() => onTabChange(key)}
            className={cn(
              "flex flex-col items-center justify-center px-2 py-1 rounded-lg transition-all",
              "min-w-0 flex-1 max-w-20",
              activeTab === key
                ? "text-accent bg-accent/10"
                : "text-text-secondary hover:text-text-primary hover:bg-border"
            )}
            aria-label={label}
          >
            <Icon className="w-5 h-5 mb-1" />
            <span className="text-xs font-medium truncate">{label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
}
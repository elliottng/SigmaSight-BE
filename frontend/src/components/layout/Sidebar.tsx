'use client';

import React from 'react';
import { Home, Layers, TrendingUp, BarChart3, FileText, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { TabKey } from './Layout';

interface SidebarProps {
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

const navigationItems = [
  {
    key: 'dashboard' as TabKey,
    icon: Home,
    label: 'Dashboard',
    description: 'Portfolio overview'
  },
  {
    key: 'positions' as TabKey,
    icon: Layers,
    label: 'Positions',
    description: 'Holdings management'
  },
  {
    key: 'risk' as TabKey,
    icon: TrendingUp,
    label: 'Risk Analytics',
    description: 'Risk metrics & factors'
  },
  {
    key: 'performance' as TabKey,
    icon: BarChart3,
    label: 'Performance',
    description: 'Historical tracking'
  },
  {
    key: 'reports' as TabKey,
    icon: FileText,
    label: 'Reports',
    description: 'Generated reports'
  },
];

export default function Sidebar({ 
  activeTab, 
  onTabChange, 
  isOpen, 
  onClose,
  className 
}: SidebarProps) {
  const handleTabChange = (tab: TabKey) => {
    onTabChange(tab);
    onClose(); // Close sidebar on mobile after selection
  };
  
  return (
    <aside className={cn(
      "fixed top-0 left-0 h-full w-64 bg-surface border-r border-border z-50 transition-transform duration-300",
      "md:translate-x-0", // Always visible on desktop
      isOpen ? "translate-x-0" : "-translate-x-full", // Slide in/out on mobile
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">Σ</span>
          </div>
          <span className="font-semibold text-lg">SigmaSight</span>
        </div>
        
        <button
          onClick={onClose}
          className="p-1 hover:bg-border rounded-lg transition-colors md:hidden"
          aria-label="Close menu"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
      
      {/* Navigation */}
      <nav className="p-4">
        <div className="space-y-2">
          {navigationItems.map(({ key, icon: Icon, label, description }) => (
            <button
              key={key}
              onClick={() => handleTabChange(key)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all",
                "text-left group hover:bg-border",
                activeTab === key
                  ? "bg-accent/10 text-accent border border-accent/20"
                  : "text-text-secondary hover:text-text-primary"
              )}
            >
              <Icon className={cn(
                "w-5 h-5 flex-shrink-0",
                activeTab === key ? "text-accent" : "text-text-secondary group-hover:text-text-primary"
              )} />
              <div className="min-w-0 flex-1">
                <div className="font-medium">{label}</div>
                <div className="text-xs text-text-muted opacity-75">{description}</div>
              </div>
            </button>
          ))}
        </div>
      </nav>
      
      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border">
        <div className="text-xs text-text-muted text-center">
          <div>SigmaSight Portfolio Analytics</div>
          <div className="mt-1">Version 2.0</div>
        </div>
      </div>
    </aside>
  );
}
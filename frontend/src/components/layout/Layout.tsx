'use client';

import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import Header from './Header';
import BottomNavigation from './BottomNavigation';
import Sidebar from './Sidebar';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export type TabKey = 'dashboard' | 'positions' | 'risk' | 'performance' | 'reports';

interface LayoutProps {
  children: React.ReactNode;
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
}

export default function Layout({ children, activeTab, onTabChange }: LayoutProps) {
  const { isLoading, isAuthenticated } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background">
        {children}
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-background text-text-primary">
      {/* Header - Desktop */}
      <Header 
        onMenuClick={() => setSidebarOpen(true)}
        className="hidden md:flex"
      />
      
      {/* Sidebar - Desktop */}
      <Sidebar 
        activeTab={activeTab}
        onTabChange={onTabChange}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        className="hidden md:block"
      />
      
      {/* Main Content */}
      <main className="flex-1 overflow-y-auto pb-16 md:pb-0 md:ml-64">
        <div className="p-4 md:p-6">
          {children}
        </div>
      </main>
      
      {/* Bottom Navigation - Mobile */}
      <BottomNavigation 
        activeTab={activeTab}
        onTabChange={onTabChange}
        className="md:hidden"
      />
      
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <Sidebar 
            activeTab={activeTab}
            onTabChange={onTabChange}
            isOpen={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            className="relative z-50"
          />
        </div>
      )}
    </div>
  );
}
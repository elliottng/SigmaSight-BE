'use client';

import React from 'react';
import { Menu, LogOut, User } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { cn } from '@/lib/utils';

interface HeaderProps {
  onMenuClick?: () => void;
  className?: string;
}

export default function Header({ onMenuClick, className }: HeaderProps) {
  const { user, logout } = useAuth();
  
  const handleLogout = () => {
    logout();
  };
  
  return (
    <header className={cn(
      "flex items-center justify-between p-4 border-b border-border bg-surface",
      className
    )}>
      {/* Left side - Logo and Menu */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="p-2 hover:bg-border rounded-lg transition-colors md:hidden"
          aria-label="Open menu"
        >
          <Menu className="w-5 h-5" />
        </button>
        
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-accent rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">Σ</span>
          </div>
          <span className="font-semibold text-lg">SigmaSight</span>
        </div>
      </div>
      
      {/* Right side - User Profile */}
      <div className="flex items-center gap-2">
        {user && (
          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-medium">{user.full_name || user.username}</p>
              <p className="text-xs text-text-secondary">{user.email}</p>
            </div>
            
            <div className="flex items-center gap-1">
              <button className="p-2 hover:bg-border rounded-lg transition-colors">
                <User className="w-5 h-5" />
              </button>
              
              <button
                onClick={handleLogout}
                className="p-2 hover:bg-border rounded-lg transition-colors text-text-secondary hover:text-status-danger"
                aria-label="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
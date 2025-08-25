'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface SelectProps {
  value: string;
  onValueChange: (value: string) => void;
  children: React.ReactNode;
}

export function Select({ value, onValueChange, children }: SelectProps) {
  return (
    <div className="relative">
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child) && child.type === SelectTrigger) {
          return React.cloneElement(child, { value, onValueChange } as any);
        }
        if (React.isValidElement(child) && child.type === SelectContent) {
          return React.cloneElement(child, { value, onValueChange } as any);
        }
        return child;
      })}
    </div>
  );
}

interface SelectTriggerProps extends React.HTMLAttributes<HTMLSelectElement> {
  value?: string;
  onValueChange?: (value: string) => void;
  children: React.ReactNode;
}

export function SelectTrigger({ className, value, onValueChange, children, ...props }: SelectTriggerProps) {
  return (
    <select
      className={cn(
        'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
        className
      )}
      value={value}
      onChange={(e) => onValueChange?.(e.target.value)}
      {...props}
    >
      {children}
    </select>
  );
}

interface SelectValueProps {
  placeholder?: string;
}

export function SelectValue({ placeholder }: SelectValueProps) {
  return <option value="" disabled>{placeholder}</option>;
}

interface SelectContentProps {
  value?: string;
  onValueChange?: (value: string) => void;
  children: React.ReactNode;
}

export function SelectContent({ children }: SelectContentProps) {
  return <>{children}</>;
}

interface SelectItemProps extends React.HTMLAttributes<HTMLOptionElement> {
  value: string;
  children: React.ReactNode;
}

export function SelectItem({ value, children, className, ...props }: SelectItemProps) {
  return (
    <option 
      value={value} 
      className={cn('relative cursor-default select-none py-1.5 px-2 text-sm', className)}
      {...props}
    >
      {children}
    </option>
  );
}
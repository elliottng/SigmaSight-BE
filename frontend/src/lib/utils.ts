import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Format currency values
export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

// Format currency with decimals
export const formatCurrencyDecimals = (value: number, decimals: number = 2): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

// Format percentage
export const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${(value * 100).toFixed(decimals)}%`
}

// Format large numbers with K, M, B suffixes
export const formatLargeNumber = (value: number): string => {
  const absValue = Math.abs(value)
  const sign = value < 0 ? '-' : ''
  
  if (absValue >= 1_000_000_000) {
    return `${sign}${(absValue / 1_000_000_000).toFixed(1)}B`
  } else if (absValue >= 1_000_000) {
    return `${sign}${(absValue / 1_000_000).toFixed(1)}M`
  } else if (absValue >= 1_000) {
    return `${sign}${(absValue / 1_000).toFixed(1)}K`
  }
  return value.toString()
}

// Get color class based on value
export const getValueColor = (value: number): string => {
  if (value > 0) return 'text-green-600'
  if (value < 0) return 'text-red-600'
  return 'text-gray-600'
}

// Get background color based on status
export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'success':
      return 'bg-green-100 text-green-800'
    case 'warning':
      return 'bg-yellow-100 text-yellow-800'
    case 'danger':
      return 'bg-red-100 text-red-800'
    case 'info':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

// Get position type display name
export const getPositionTypeDisplay = (type: string): string => {
  switch (type) {
    case 'LONG':
      return 'Long Stock'
    case 'SHORT':
      return 'Short Stock'
    case 'LC':
      return 'Long Call'
    case 'LP':
      return 'Long Put'
    case 'SC':
      return 'Short Call'
    case 'SP':
      return 'Short Put'
    default:
      return type
  }
}

// Get position type color
export const getPositionTypeColor = (type: string): string => {
  switch (type) {
    case 'LONG':
    case 'LC':
    case 'LP':
      return 'text-green-600 bg-green-50'
    case 'SHORT':
    case 'SC':
    case 'SP':
      return 'text-red-600 bg-red-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

// Format date
export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

// Format date and time
export const formatDateTime = (dateString: string): string => {
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Validate email
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// Debounce function
export const debounce = <T extends (...args: any[]) => void>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

// Calculate days to expiration
export const daysToExpiration = (expirationDate: string): number => {
  const today = new Date()
  const expiration = new Date(expirationDate)
  const timeDiff = expiration.getTime() - today.getTime()
  return Math.ceil(timeDiff / (1000 * 3600 * 24))
}

// Get expiration urgency color
export const getExpirationUrgency = (expirationDate: string): string => {
  const days = daysToExpiration(expirationDate)
  if (days <= 1) return 'text-red-600 bg-red-50'
  if (days <= 7) return 'text-yellow-600 bg-yellow-50'
  if (days <= 30) return 'text-blue-600 bg-blue-50'
  return 'text-gray-600 bg-gray-50'
}

// Safe divide to avoid division by zero
export const safeDivide = (numerator: number, denominator: number): number => {
  return denominator === 0 ? 0 : numerator / denominator
}

// Round to specified decimal places
export const roundTo = (value: number, decimals: number): number => {
  return Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals)
}

// Generate random ID
export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9)
}
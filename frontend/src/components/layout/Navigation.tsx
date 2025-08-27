'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import { useAuth } from '../../contexts/AuthContext'
import {
  LayoutDashboard,
  TrendingUp,
  Shield,
  FileText,
  Settings,
  User,
  LogOut,
  Menu,
  X,
  AlertTriangle,
  BarChart3,
} from 'lucide-react'
import { cn } from '../../lib/utils'

const navigationItems = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    description: 'Portfolio overview and key metrics',
  },
  {
    name: 'Positions',
    href: '/positions',
    icon: TrendingUp,
    description: 'View and manage portfolio positions',
  },
  {
    name: 'Risk Analytics',
    href: '/risk',
    icon: Shield,
    description: 'Greeks, factors, and risk metrics',
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: FileText,
    description: 'Generate and view risk reports',
  },
  {
    name: 'Market Data',
    href: '/market',
    icon: BarChart3,
    description: 'Real-time quotes and market data',
  },
]

interface NavigationProps {
  alertCount?: number
}

export default function Navigation({ alertCount = 0 }: NavigationProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const pathname = usePathname()
  const { user, logout } = useAuth()

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard' || pathname === '/'
    }
    return pathname.startsWith(href)
  }

  return (
    <>
      {/* Desktop Sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto border-r border-gray-200 bg-white px-6 pb-4">
          {/* Logo */}
          <div className="flex h-16 shrink-0 items-center">
            <Link href="/dashboard" className="flex items-center gap-3">
              <Image
                src="/assets/sigmasight-logo.png"
                alt="SigmaSight Logo"
                width={32}
                height={32}
                className="h-8 w-8"
              />
              <span className="text-xl font-bold text-gray-900">SigmaSight</span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigationItems.map((item) => (
                    <li key={item.name}>
                      <Link
                        href={item.href}
                        className={cn(
                          isActive(item.href)
                            ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                            : 'text-gray-700 hover:text-blue-700 hover:bg-gray-50',
                          'group flex gap-x-3 rounded-l-md py-2 pl-2 pr-3 text-sm leading-6 font-medium'
                        )}
                      >
                        <item.icon
                          className={cn(
                            isActive(item.href) ? 'text-blue-700' : 'text-gray-400 group-hover:text-blue-700',
                            'h-6 w-6 shrink-0'
                          )}
                        />
                        <div className="flex flex-col">
                          <span>{item.name}</span>
                          <span className="text-xs text-gray-500 group-hover:text-gray-600">
                            {item.description}
                          </span>
                        </div>
                        {item.name === 'Dashboard' && alertCount > 0 && (
                          <span className="ml-auto flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-red-600 text-xs font-medium text-white">
                            {alertCount > 9 ? '9+' : alertCount}
                          </span>
                        )}
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>

              {/* User Menu */}
              <li className="mt-auto">
                <div className="border-t border-gray-200 pt-4">
                  <div className="flex items-center gap-x-4 px-2 py-3 text-sm font-medium text-gray-700">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white">
                      <User className="h-4 w-4" />
                    </div>
                    <div className="flex-1 overflow-hidden">
                      <p className="truncate">{user?.full_name}</p>
                      <p className="truncate text-xs text-gray-500">{user?.email}</p>
                    </div>
                  </div>
                  <div className="mt-2 space-y-1">
                    <Link
                      href="/settings"
                      className="group flex items-center gap-x-3 rounded-md px-2 py-2 text-sm leading-6 font-medium text-gray-700 hover:text-blue-700 hover:bg-gray-50"
                    >
                      <Settings className="h-4 w-4 text-gray-400 group-hover:text-blue-700" />
                      Settings
                    </Link>
                    <button
                      onClick={logout}
                      className="group flex w-full items-center gap-x-3 rounded-md px-2 py-2 text-sm leading-6 font-medium text-gray-700 hover:text-red-700 hover:bg-red-50"
                    >
                      <LogOut className="h-4 w-4 text-gray-400 group-hover:text-red-700" />
                      Sign out
                    </button>
                  </div>
                </div>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* Mobile menu button */}
      <div className="sticky top-0 z-40 flex items-center gap-x-6 bg-white px-4 py-4 shadow-sm sm:px-6 lg:hidden">
        <button
          type="button"
          className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
          onClick={() => setIsMobileMenuOpen(true)}
        >
          <span className="sr-only">Open sidebar</span>
          <Menu className="h-6 w-6" />
        </button>
        <div className="flex-1 text-sm font-semibold leading-6 text-gray-900">
          <Link href="/dashboard" className="flex items-center gap-2">
            <Image
              src="/assets/sigmasight-logo.png"
              alt="SigmaSight Logo"
              width={24}
              height={24}
              className="h-6 w-6"
            />
            SigmaSight
          </Link>
        </div>
        {alertCount > 0 && (
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <span className="text-sm font-medium text-red-600">{alertCount}</span>
          </div>
        )}
      </div>

      {/* Mobile menu */}
      {isMobileMenuOpen && (
        <div className="relative z-50 lg:hidden">
          <div className="fixed inset-0 bg-gray-900/80" onClick={() => setIsMobileMenuOpen(false)} />
          <div className="fixed inset-0 flex">
            <div className="relative mr-16 flex w-full max-w-xs flex-1">
              <div className="absolute left-full top-0 flex w-16 justify-center pt-5">
                <button
                  type="button"
                  className="-m-2.5 p-2.5"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <span className="sr-only">Close sidebar</span>
                  <X className="h-6 w-6 text-white" />
                </button>
              </div>
              <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4">
                {/* Mobile Logo */}
                <div className="flex h-16 shrink-0 items-center">
                  <Link href="/dashboard" className="flex items-center gap-3">
                    <Image
                      src="/assets/sigmasight-logo.png"
                      alt="SigmaSight Logo"
                      width={32}
                      height={32}
                      className="h-8 w-8"
                    />
                    <span className="text-xl font-bold text-gray-900">SigmaSight</span>
                  </Link>
                </div>

                {/* Mobile Navigation */}
                <nav className="flex flex-1 flex-col">
                  <ul role="list" className="flex flex-1 flex-col gap-y-7">
                    <li>
                      <ul role="list" className="-mx-2 space-y-1">
                        {navigationItems.map((item) => (
                          <li key={item.name}>
                            <Link
                              href={item.href}
                              className={cn(
                                isActive(item.href)
                                  ? 'bg-blue-50 text-blue-700'
                                  : 'text-gray-700 hover:text-blue-700 hover:bg-gray-50',
                                'group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-medium'
                              )}
                              onClick={() => setIsMobileMenuOpen(false)}
                            >
                              <item.icon
                                className={cn(
                                  isActive(item.href) ? 'text-blue-700' : 'text-gray-400 group-hover:text-blue-700',
                                  'h-6 w-6 shrink-0'
                                )}
                              />
                              {item.name}
                              {item.name === 'Dashboard' && alertCount > 0 && (
                                <span className="ml-auto flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-red-600 text-xs font-medium text-white">
                                  {alertCount > 9 ? '9+' : alertCount}
                                </span>
                              )}
                            </Link>
                          </li>
                        ))}
                      </ul>
                    </li>

                    {/* Mobile User Menu */}
                    <li className="mt-auto">
                      <div className="border-t border-gray-200 pt-4">
                        <div className="flex items-center gap-x-4 px-2 py-3 text-sm font-medium text-gray-700">
                          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white">
                            <User className="h-4 w-4" />
                          </div>
                          <div className="flex-1">
                            <p>{user?.full_name}</p>
                            <p className="text-xs text-gray-500">{user?.email}</p>
                          </div>
                        </div>
                        <div className="mt-2 space-y-1">
                          <Link
                            href="/settings"
                            className="group flex items-center gap-x-3 rounded-md px-2 py-2 text-sm leading-6 font-medium text-gray-700 hover:text-blue-700 hover:bg-gray-50"
                            onClick={() => setIsMobileMenuOpen(false)}
                          >
                            <Settings className="h-4 w-4 text-gray-400 group-hover:text-blue-700" />
                            Settings
                          </Link>
                          <button
                            onClick={() => {
                              setIsMobileMenuOpen(false)
                              logout()
                            }}
                            className="group flex w-full items-center gap-x-3 rounded-md px-2 py-2 text-sm leading-6 font-medium text-gray-700 hover:text-red-700 hover:bg-red-50"
                          >
                            <LogOut className="h-4 w-4 text-gray-400 group-hover:text-red-700" />
                            Sign out
                          </button>
                        </div>
                      </div>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
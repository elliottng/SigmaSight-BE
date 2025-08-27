'use client'

import { useState, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'
import {
  Search,
  Filter,
  SortAsc,
  SortDesc,
  MoreHorizontal,
  Edit,
  Trash2,
  TrendingUp,
  TrendingDown,
} from 'lucide-react'
import { 
  formatCurrency, 
  formatPercentage, 
  getPositionTypeDisplay, 
  getPositionTypeColor,
  getValueColor,
  daysToExpiration,
  getExpirationUrgency,
  cn 
} from '../../lib/utils'
import type { Position, PositionType } from '../../lib/types'

interface PositionTableProps {
  positions: Position[]
  loading?: boolean
  onEdit?: (position: Position) => void
  onDelete?: (positionId: string) => void
}

type SortField = 'ticker' | 'value' | 'pnl' | 'pnl_percent' | 'exposure' | 'expiration'
type SortDirection = 'asc' | 'desc'

export default function PositionTable({ 
  positions, 
  loading = false, 
  onEdit, 
  onDelete 
}: PositionTableProps) {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedType, setSelectedType] = useState<PositionType | 'ALL'>('ALL')
  const [sortField, setSortField] = useState<SortField>('value')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')

  const positionTypes: (PositionType | 'ALL')[] = ['ALL', 'LONG', 'SHORT', 'LC', 'LP', 'SC', 'SP']

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return null
    return sortDirection === 'asc' ? 
      <SortAsc className="h-4 w-4 ml-1" /> : 
      <SortDesc className="h-4 w-4 ml-1" />
  }

  const filteredAndSortedPositions = useMemo(() => {
    let filtered = positions.filter(position => {
      const matchesSearch = position.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           position.name.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesType = selectedType === 'ALL' || position.type === selectedType
      return matchesSearch && matchesType
    })

    return filtered.sort((a, b) => {
      let aValue: any, bValue: any

      switch (sortField) {
        case 'ticker':
          aValue = a.ticker
          bValue = b.ticker
          break
        case 'value':
          aValue = a.value
          bValue = b.value
          break
        case 'pnl':
          aValue = a.pnl
          bValue = b.pnl
          break
        case 'pnl_percent':
          aValue = a.pnl_percent
          bValue = b.pnl_percent
          break
        case 'exposure':
          aValue = a.exposure || a.value
          bValue = b.exposure || b.value
          break
        case 'expiration':
          aValue = a.expiration ? new Date(a.expiration).getTime() : 0
          bValue = b.expiration ? new Date(b.expiration).getTime() : 0
          break
        default:
          return 0
      }

      if (typeof aValue === 'string') {
        const result = aValue.localeCompare(bValue)
        return sortDirection === 'asc' ? result : -result
      }

      const result = aValue - bValue
      return sortDirection === 'asc' ? result : -result
    })
  }, [positions, searchTerm, selectedType, sortField, sortDirection])

  const totalValue = positions.reduce((sum, position) => sum + position.value, 0)
  const totalPnl = positions.reduce((sum, position) => sum + position.pnl, 0)

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Positions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-12 bg-gray-300 rounded"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle>Positions ({positions.length})</CardTitle>
          <div className="text-sm text-gray-600">
            Total: {formatCurrency(totalValue)} • P&L: {' '}
            <span className={getValueColor(totalPnl)}>
              {formatCurrency(totalPnl)} ({formatPercentage(totalPnl / totalValue)})
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Search positions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value as PositionType | 'ALL')}
              className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {positionTypes.map(type => (
                <option key={type} value={type}>
                  {type === 'ALL' ? 'All Types' : getPositionTypeDisplay(type)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('ticker')}
                    className="font-semibold text-gray-700 hover:text-gray-900 p-0 h-auto"
                  >
                    Symbol
                    {getSortIcon('ticker')}
                  </Button>
                </th>
                <th className="text-left py-3 px-2">Type</th>
                <th className="text-right py-3 px-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('value')}
                    className="font-semibold text-gray-700 hover:text-gray-900 p-0 h-auto ml-auto"
                  >
                    Value
                    {getSortIcon('value')}
                  </Button>
                </th>
                <th className="text-right py-3 px-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('pnl')}
                    className="font-semibold text-gray-700 hover:text-gray-900 p-0 h-auto ml-auto"
                  >
                    P&L
                    {getSortIcon('pnl')}
                  </Button>
                </th>
                <th className="text-right py-3 px-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('pnl_percent')}
                    className="font-semibold text-gray-700 hover:text-gray-900 p-0 h-auto ml-auto"
                  >
                    P&L %
                    {getSortIcon('pnl_percent')}
                  </Button>
                </th>
                <th className="text-right py-3 px-2">Quantity</th>
                <th className="text-right py-3 px-2">Price</th>
                <th className="text-right py-3 px-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSort('expiration')}
                    className="font-semibold text-gray-700 hover:text-gray-900 p-0 h-auto ml-auto"
                  >
                    Expiry
                    {getSortIcon('expiration')}
                  </Button>
                </th>
                <th className="text-center py-3 px-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAndSortedPositions.map((position) => (
                <tr key={position.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-2">
                    <div>
                      <div className="font-semibold text-gray-900">{position.ticker}</div>
                      <div className="text-sm text-gray-600 truncate max-w-[120px]">
                        {position.name}
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-2">
                    <span className={cn(
                      'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                      getPositionTypeColor(position.type)
                    )}>
                      {getPositionTypeDisplay(position.type)}
                    </span>
                  </td>
                  <td className="py-3 px-2 text-right font-mono">
                    {formatCurrency(position.value)}
                  </td>
                  <td className="py-3 px-2 text-right">
                    <div className={cn('flex items-center justify-end', getValueColor(position.pnl))}>
                      {position.pnl > 0 ? (
                        <TrendingUp className="h-3 w-3 mr-1" />
                      ) : position.pnl < 0 ? (
                        <TrendingDown className="h-3 w-3 mr-1" />
                      ) : null}
                      <span className="font-mono">{formatCurrency(position.pnl)}</span>
                    </div>
                  </td>
                  <td className="py-3 px-2 text-right">
                    <span className={cn('font-mono', getValueColor(position.pnl))}>
                      {formatPercentage(position.pnl_percent / 100)}
                    </span>
                  </td>
                  <td className="py-3 px-2 text-right font-mono">
                    {position.quantity.toLocaleString()}
                  </td>
                  <td className="py-3 px-2 text-right font-mono">
                    {formatCurrency(position.price)}
                  </td>
                  <td className="py-3 px-2 text-right">
                    {position.expiration ? (
                      <div>
                        <span className={cn(
                          'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                          getExpirationUrgency(position.expiration)
                        )}>
                          {daysToExpiration(position.expiration)}d
                        </span>
                        <div className="text-xs text-gray-500 mt-1">
                          {new Date(position.expiration).toLocaleDateString()}
                        </div>
                      </div>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                  <td className="py-3 px-2">
                    <div className="flex items-center justify-center space-x-1">
                      {onEdit && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onEdit(position)}
                          className="h-8 w-8 p-0"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                      )}
                      {onDelete && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onDelete(position.id)}
                          className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0"
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredAndSortedPositions.length === 0 && (
            <div className="text-center py-8">
              <div className="text-gray-500">
                {searchTerm || selectedType !== 'ALL' ? 
                  'No positions match your filters' : 
                  'No positions found'
                }
              </div>
              {(searchTerm || selectedType !== 'ALL') && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSearchTerm('')
                    setSelectedType('ALL')
                  }}
                  className="mt-2"
                >
                  Clear filters
                </Button>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
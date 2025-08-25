'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { formatCurrency, formatPercent } from '@/lib/utils';

interface Position {
  id: string;
  symbol: string;
  name?: string;
  quantity: number;
  market_value: number;
  weight: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
  sector?: string;
  industry?: string;
  price: number;
}

interface PositionsTableProps {
  positions: Position[];
  portfolioId: string;
}

export function PositionsTable({ positions, portfolioId }: PositionsTableProps) {
  const [sortField, setSortField] = useState<keyof Position>('weight');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [selectedPositions, setSelectedPositions] = useState<string[]>([]);

  if (!positions || positions.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center py-8">
          <p className="text-gray-500">No positions found for this portfolio.</p>
        </div>
      </Card>
    );
  }

  const handleSort = (field: keyof Position) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedPositions = [...positions].sort((a, b) => {
    const aVal = a[sortField];
    const bVal = b[sortField];
    
    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return sortDirection === 'asc' 
        ? aVal.localeCompare(bVal)
        : bVal.localeCompare(aVal);
    }
    
    const aNum = Number(aVal) || 0;
    const bNum = Number(bVal) || 0;
    
    return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
  });

  const togglePositionSelection = (positionId: string) => {
    setSelectedPositions(prev => 
      prev.includes(positionId)
        ? prev.filter(id => id !== positionId)
        : [...prev, positionId]
    );
  };

  const SortButton = ({ field, children }: { field: keyof Position; children: React.ReactNode }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center space-x-1 hover:text-blue-600 transition-colors"
    >
      <span>{children}</span>
      {sortField === field && (
        <span className="text-xs">
          {sortDirection === 'asc' ? '↑' : '↓'}
        </span>
      )}
    </button>
  );

  return (
    <Card className="overflow-hidden">
      {/* Table Header Actions */}
      <div className="p-4 border-b bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              {positions.length} positions
            </span>
            {selectedPositions.length > 0 && (
              <span className="text-sm text-blue-600">
                {selectedPositions.length} selected
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {selectedPositions.length > 0 && (
              <Button variant="outline" size="sm">
                Bulk Actions
              </Button>
            )}
            <Button variant="outline" size="sm">
              Export
            </Button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left">
                <input
                  type="checkbox"
                  checked={selectedPositions.length === positions.length}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedPositions(positions.map(p => p.id));
                    } else {
                      setSelectedPositions([]);
                    }
                  }}
                  className="rounded"
                />
              </th>
              <th className="px-4 py-3 text-left font-medium text-gray-900">
                <SortButton field="symbol">Symbol</SortButton>
              </th>
              <th className="px-4 py-3 text-right font-medium text-gray-900">
                <SortButton field="quantity">Quantity</SortButton>
              </th>
              <th className="px-4 py-3 text-right font-medium text-gray-900">
                <SortButton field="price">Price</SortButton>
              </th>
              <th className="px-4 py-3 text-right font-medium text-gray-900">
                <SortButton field="market_value">Market Value</SortButton>
              </th>
              <th className="px-4 py-3 text-right font-medium text-gray-900">
                <SortButton field="weight">Weight</SortButton>
              </th>
              <th className="px-4 py-3 text-right font-medium text-gray-900">
                <SortButton field="unrealized_pnl">P&L</SortButton>
              </th>
              <th className="px-4 py-3 text-left font-medium text-gray-900">
                <SortButton field="sector">Sector</SortButton>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sortedPositions.map((position) => (
              <tr 
                key={position.id}
                className={`hover:bg-gray-50 transition-colors ${
                  selectedPositions.includes(position.id) ? 'bg-blue-50' : ''
                }`}
              >
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedPositions.includes(position.id)}
                    onChange={() => togglePositionSelection(position.id)}
                    className="rounded"
                  />
                </td>
                <td className="px-4 py-3">
                  <div>
                    <div className="font-medium text-gray-900">{position.symbol}</div>
                    {position.name && (
                      <div className="text-sm text-gray-500 truncate max-w-xs">
                        {position.name}
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3 text-right font-mono">
                  {position.quantity.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right font-mono">
                  {formatCurrency(position.price)}
                </td>
                <td className="px-4 py-3 text-right font-mono">
                  {formatCurrency(position.market_value)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatPercent(position.weight)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div className="flex flex-col">
                    <span className={position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                      {formatCurrency(position.unrealized_pnl)}
                    </span>
                    <span className={`text-xs ${position.unrealized_pnl_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatPercent(position.unrealized_pnl_pct)}
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="space-y-1">
                    <div className="text-sm font-medium text-gray-900">
                      {position.sector || 'N/A'}
                    </div>
                    {position.industry && (
                      <div className="text-xs text-gray-500">
                        {position.industry}
                      </div>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

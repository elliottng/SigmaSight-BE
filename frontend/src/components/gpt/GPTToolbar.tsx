'use client';

import React, { useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { useGPTAgent, GPTResponse } from '@/hooks/useGPTAgent';
import Button from '@/components/ui/Button';
import { Card, CardHeader, CardContent } from '@/components/ui/Card';
import { InsightCard, FactorCard, ActionItems, GapAlert } from './InsightCard';
import ReactMarkdown from 'react-markdown';
import { cn } from '@/lib/utils';

interface GPTToolbarProps {
  portfolioId?: string;
  contextData?: {
    selectedPositions?: string[];
    dateRange?: { from: Date; to: Date };
    filters?: Record<string, any>;
  };
  className?: string;
}

export function GPTToolbar({ portfolioId, contextData, className }: GPTToolbarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [prompt, setPrompt] = useState('');
  const { 
    analyze, 
    analysis, 
    loading, 
    error, 
    healthStatus, 
    isOnline,
    clearAnalysis 
  } = useGPTAgent();

  const handleAnalyze = useCallback(async () => {
    if (!portfolioId || !prompt.trim()) return;

    try {
      await analyze({
        portfolio_id: portfolioId,
        user_context: {
          prompt: prompt.trim(),
          selected_positions: contextData?.selectedPositions,
          date_range: contextData?.dateRange,
          page_context: typeof window !== 'undefined' ? window.location.pathname : undefined
        }
      });
    } catch (err) {
      // Error is already handled in the hook
      console.error('Analysis failed:', err);
    }
  }, [portfolioId, prompt, contextData, analyze]);

  const handleClear = useCallback(() => {
    setPrompt('');
    clearAnalysis();
  }, [clearAnalysis]);

  const handleQuickPrompt = useCallback((quickPrompt: string) => {
    setPrompt(quickPrompt);
  }, []);

  // Quick prompts for common analysis requests
  const quickPrompts = [
    'Analyze my portfolio risk and concentration',
    'What are my biggest exposures?',
    'Show me optimization opportunities',
    'Identify correlation risks',
  ];

  return (
    <>
      {/* Floating Toggle Button */}
      <div className={cn(
        'fixed bottom-6 right-6 z-50',
        className
      )}>
        <Button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            'rounded-full w-14 h-14 shadow-lg transition-all duration-200',
            'hover:scale-110 focus:scale-105'
          )}
          variant={isOnline ? "primary" : "danger"}
          size="lg"
        >
          {isOnline ? "🤖" : "🔴"}
        </Button>
      </div>

      {/* Collapsible Toolbar */}
      {isOpen && (
        <Card className={cn(
          'fixed bottom-24 right-6 w-96 max-w-[calc(100vw-3rem)] max-h-[600px] shadow-2xl z-40',
          'animate-in slide-in-from-bottom-2 fade-in duration-200'
        )}>
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-base">Portfolio AI Assistant</h3>
                <div className="flex items-center space-x-2 mt-1">
                  <div className={cn(
                    'w-2 h-2 rounded-full',
                    isOnline ? 'bg-green-500' : 'bg-red-500'
                  )} />
                  <span className="text-xs text-muted-foreground">
                    {isOnline ? 'AI Assistant Online' : 'AI Assistant Offline'}
                  </span>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
                className="h-8 w-8 p-0"
              >
                ✕
              </Button>
            </div>
          </CardHeader>

          <CardContent className="space-y-4 max-h-[500px] overflow-y-auto">
            {/* Context Display */}
            {portfolioId && (
              <div className="text-sm text-muted-foreground space-y-1 p-2 bg-muted/50 rounded">
                <div>Portfolio: <span className="font-mono">{portfolioId.slice(0, 8)}...</span></div>
                {contextData?.selectedPositions?.length && (
                  <div>{contextData.selectedPositions.length} positions selected</div>
                )}
                {contextData?.dateRange && (
                  <div>
                    Date range: {contextData.dateRange.from.toLocaleDateString()} - {contextData.dateRange.to.toLocaleDateString()}
                  </div>
                )}
              </div>
            )}

            {/* Quick Prompts */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Quick Analysis:</h4>
              <div className="grid grid-cols-1 gap-2">
                {quickPrompts.map((quickPrompt, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => handleQuickPrompt(quickPrompt)}
                    className="text-left justify-start h-auto py-2 px-3"
                    disabled={!isOnline}
                  >
                    <span className="text-xs">{quickPrompt}</span>
                  </Button>
                ))}
              </div>
            </div>

            {/* Input Area */}
            <div className="space-y-2">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Ask about this portfolio... (e.g., 'What are the main risk factors?' or 'Analyze my position concentration')"
                rows={3}
                disabled={!isOnline}
                className={cn(
                  'w-full p-3 text-sm border rounded-md resize-none',
                  'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                  'disabled:bg-muted disabled:cursor-not-allowed'
                )}
              />
            </div>

            {/* Actions */}
            <div className="flex space-x-2">
              <Button
                onClick={handleAnalyze}
                disabled={!prompt.trim() || loading || !isOnline}
                className="flex-1"
                loading={loading}
              >
                {loading ? "Analyzing..." : "Analyze"}
              </Button>
              <Button
                variant="outline"
                onClick={handleClear}
                disabled={loading}
              >
                Clear
              </Button>
            </div>

            {/* Error Display */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded">
                <div className="flex items-start">
                  <span className="text-red-600 mr-2">❌</span>
                  <div>
                    <h4 className="text-sm font-medium text-red-800">Analysis Failed</h4>
                    <p className="text-sm text-red-700 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Results Display */}
            {analysis && (
              <div className="space-y-3 border-t pt-4">
                {/* Summary */}
                {analysis.summary_markdown && (
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown
                      components={{
                        h1: ({children}) => <h4 className="text-sm font-semibold mb-2">{children}</h4>,
                        h2: ({children}) => <h5 className="text-xs font-medium mb-1">{children}</h5>,
                        h3: ({children}) => <h6 className="text-xs font-medium mb-1">{children}</h6>,
                        p: ({children}) => <p className="text-xs mb-2 leading-relaxed">{children}</p>,
                        ul: ({children}) => <ul className="text-xs space-y-1 mb-2">{children}</ul>,
                        li: ({children}) => <li className="flex items-start"><span className="mr-1">•</span><span>{children}</span></li>,
                      }}
                    >
                      {analysis.summary_markdown}
                    </ReactMarkdown>
                  </div>
                )}

                {/* Insights Cards */}
                <div className="space-y-3">
                  {analysis.machine_readable.snapshot && (
                    <InsightCard
                      title="Portfolio Metrics"
                      data={analysis.machine_readable.snapshot}
                      compact
                    />
                  )}

                  {analysis.machine_readable.concentration && (
                    <InsightCard
                      title="Concentration"
                      data={analysis.machine_readable.concentration}
                      compact
                    />
                  )}

                  {analysis.machine_readable.factors && analysis.machine_readable.factors.length > 0 && (
                    <FactorCard
                      factors={analysis.machine_readable.factors}
                      compact
                    />
                  )}

                  {analysis.machine_readable.actions && analysis.machine_readable.actions.length > 0 && (
                    <ActionItems
                      actions={analysis.machine_readable.actions}
                      compact
                    />
                  )}

                  {analysis.machine_readable.gaps && analysis.machine_readable.gaps.length > 0 && (
                    <GapAlert
                      gaps={analysis.machine_readable.gaps}
                    />
                  )}
                </div>
              </div>
            )}

            {/* Status Footer */}
            <div className="text-xs text-center text-muted-foreground border-t pt-3">
              {healthStatus?.backend_connected ? (
                <span className="text-green-600">✅ Connected to SigmaSight Backend</span>
              ) : (
                <span className="text-red-600">🔴 Backend Connection Failed</span>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </>
  );
}

export default GPTToolbar;
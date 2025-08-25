'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { useGPTAgent, GPTResponse } from '@/hooks/useGPTAgent';
import Button from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { InsightCard, FactorCard, ActionItems, GapAlert } from '@/components/gpt/InsightCard';
import ReactMarkdown from 'react-markdown';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { cn } from '@/lib/utils';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  analysis?: GPTResponse;
  timestamp: Date;
}

interface ChatInputProps {
  onSubmit: (message: string) => void;
  loading: boolean;
  disabled: boolean;
}

function ChatInput({ onSubmit, loading, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      onSubmit(input.trim());
      setInput('');
    }
  }, [input, loading, onSubmit]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [input]);

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex space-x-4">
        <div className="flex-1">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything about your portfolio... (e.g., 'What are my biggest risk factors?' or 'How concentrated is my portfolio?')"
            className={cn(
              'w-full p-4 border rounded-lg resize-none min-h-[60px] max-h-[120px]',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
              'disabled:bg-gray-50 disabled:cursor-not-allowed'
            )}
            disabled={disabled}
            rows={2}
          />
        </div>
        <div className="flex flex-col justify-end">
          <Button
            type="submit"
            disabled={!input.trim() || loading || disabled}
            loading={loading}
            className="px-6"
          >
            Send
          </Button>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-2">
        <span className="text-sm text-gray-500">Try:</span>
        {[
          'Analyze my portfolio risk',
          'What are my factor exposures?',
          'Show me concentration metrics',
          'Identify correlation risks'
        ].map((suggestion, index) => (
          <button
            key={index}
            onClick={() => setInput(suggestion)}
            disabled={loading || disabled}
            className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full transition-colors disabled:opacity-50"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </form>
  );
}

interface ChatMessageProps {
  message: ChatMessage;
}

function ChatMessage({ message }: ChatMessageProps) {
  if (message.type === 'user') {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-3xl bg-blue-500 text-white p-4 rounded-lg">
          <p className="whitespace-pre-wrap">{message.content}</p>
          <p className="text-xs text-blue-100 mt-2">
            {message.timestamp.toLocaleTimeString()}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-6">
      <div className="max-w-4xl w-full">
        <div className="flex items-center mb-2">
          <div className="w-8 h-8 bg-gray-600 text-white rounded-full flex items-center justify-center mr-3">
            🤖
          </div>
          <span className="text-sm text-gray-500">
            AI Assistant • {message.timestamp.toLocaleTimeString()}
          </span>
        </div>
        
        <div className="ml-11 space-y-4">
          {/* Text Response */}
          <Card>
            <CardContent className="p-4">
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            </CardContent>
          </Card>

          {/* Analysis Results */}
          {message.analysis && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Portfolio Metrics */}
              {message.analysis.machine_readable.snapshot && (
                <InsightCard
                  title="Portfolio Overview"
                  data={message.analysis.machine_readable.snapshot}
                />
              )}

              {/* Concentration Metrics */}
              {message.analysis.machine_readable.concentration && (
                <InsightCard
                  title="Concentration Analysis"
                  data={message.analysis.machine_readable.concentration}
                />
              )}

              {/* Factor Exposures */}
              {message.analysis.machine_readable.factors && message.analysis.machine_readable.factors.length > 0 && (
                <div className="lg:col-span-2">
                  <FactorCard factors={message.analysis.machine_readable.factors} />
                </div>
              )}

              {/* Action Items */}
              {message.analysis.machine_readable.actions && message.analysis.machine_readable.actions.length > 0 && (
                <ActionItems
                  actions={message.analysis.machine_readable.actions}
                  className="lg:col-span-2"
                />
              )}

              {/* Data Gaps */}
              {message.analysis.machine_readable.gaps && message.analysis.machine_readable.gaps.length > 0 && (
                <GapAlert
                  gaps={message.analysis.machine_readable.gaps}
                  className="lg:col-span-2"
                />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  const searchParams = useSearchParams();
  const portfolioId = searchParams.get('portfolio') || 'a3209353-9ed5-4885-81e8-d4bbc995f96c'; // Demo portfolio fallback
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentPortfolio, setCurrentPortfolio] = useState<string>(portfolioId);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { 
    analyze, 
    loading, 
    error, 
    healthStatus, 
    isOnline 
  } = useGPTAgent();

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Add initial welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{
        id: '1',
        type: 'assistant',
        content: `# Welcome to SigmaSight AI Assistant! 🤖

I'm here to help you analyze your portfolio with real-time insights powered by your backend data.

**What I can do:**
- Analyze portfolio risk and performance metrics
- Identify concentration and correlation risks
- Explain factor exposures and market sensitivities
- Provide actionable recommendations for portfolio optimization
- Answer questions about specific positions or market scenarios

**Current Portfolio:** \`${currentPortfolio.slice(0, 8)}...\`

Feel free to ask me anything about your portfolio! For example:
- "What are my biggest risk factors?"
- "How concentrated is my portfolio?"
- "Show me my factor exposures"
- "What positions have the highest correlation?"`,
        timestamp: new Date()
      }]);
    }
  }, [currentPortfolio, messages.length]);

  const handleSendMessage = useCallback(async (content: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const analysis = await analyze({
        portfolio_id: currentPortfolio,
        user_context: {
          prompt: content,
          page_context: 'chat_page'
        }
      });

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: analysis.summary_markdown || 'Analysis completed successfully.',
        analysis,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `I apologize, but I encountered an error while analyzing your request: **${err instanceof Error ? err.message : 'Unknown error'}**

Please try again or rephrase your question. Make sure the GPT agent service is running and connected to the backend.`,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    }
  }, [analyze, currentPortfolio]);

  const handleClearChat = useCallback(() => {
    setMessages([]);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b p-6 z-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Portfolio AI Chat</h1>
              <div className="flex items-center space-x-4 mt-2">
                <div className="flex items-center space-x-2">
                  <div className={cn(
                    'w-2 h-2 rounded-full',
                    isOnline ? 'bg-green-500' : 'bg-red-500'
                  )} />
                  <span className="text-sm text-gray-600">
                    {isOnline ? 'AI Assistant Connected' : 'AI Assistant Offline'}
                  </span>
                </div>
                
                <div className="text-sm text-gray-500">
                  Portfolio: <span className="font-mono">{currentPortfolio.slice(0, 8)}...</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {messages.length > 1 && (
                <Button
                  variant="outline"
                  onClick={handleClearChat}
                  disabled={loading}
                >
                  Clear Chat
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="p-6 pb-32">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          
          {loading && (
            <div className="flex justify-start mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-600 text-white rounded-full flex items-center justify-center">
                  🤖
                </div>
                <div className="flex items-center space-x-2">
                  <LoadingSpinner size="sm" />
                  <span className="text-gray-600">AI is analyzing your portfolio...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input - Fixed at bottom */}
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t p-6">
          <div className="max-w-6xl mx-auto">
            <ChatInput
              onSubmit={handleSendMessage}
              loading={loading}
              disabled={!isOnline}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
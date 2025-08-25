import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function ChatPage() {
  const router = useRouter();
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Array<{text: string, sender: 'user' | 'bot'}>>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPortfolio, setSelectedPortfolio] = useState<string>('');

  // Handle portfolio parameter from URL
  useEffect(() => {
    if (router.query.portfolio && typeof router.query.portfolio === 'string') {
      setSelectedPortfolio(router.query.portfolio);
      // Add initial context message
      const portfolioNames: Record<string, string> = {
        'a3209353-9ed5-4885-81e8-d4bbc995f96c': 'Demo Individual Portfolio',
        '14e7f420-b096-4e2e-8cc2-531caf434c05': 'Demo High Net Worth Portfolio',
        'cf890da7-7b74-4cb4-acba-2205fdd9dff4': 'Demo Hedge Fund Portfolio',
      };
      const portfolioName = portfolioNames[router.query.portfolio] || 'Selected Portfolio';
      setMessages([{
        text: `I'm ready to analyze ${portfolioName}. What would you like to know about this portfolio's performance, risk profile, or investment strategy?`,
        sender: 'bot'
      }]);
    }
  }, [router.query.portfolio]);

  const handleSendMessage = async () => {
    if (!message.trim()) return;
    
    const userMessage = message.trim();
    setMessage('');
    setMessages(prev => [...prev, { text: userMessage, sender: 'user' }]);
    setIsLoading(true);

    try {
      // Call GPT service API (currently direct integration)
      const response = await fetch('/api/gpt/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userMessage,
          portfolio_id: selectedPortfolio || undefined
        })
      });
      
      const data = await response.json();
      setMessages(prev => [...prev, { text: data.response || 'Sorry, I encountered an error.', sender: 'bot' }]);
    } catch (error) {
      // Fallback to demo response
      setTimeout(() => {
        setMessages(prev => [...prev, { 
          text: `I received your message: "${userMessage}". This is a demo response - the GPT agent backend will be connected soon!`, 
          sender: 'bot' 
        }]);
      }, 1000);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', padding: '16px' }}>
      <div style={{ maxWidth: '1024px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold', color: '#111827', marginBottom: '2rem' }}>
          GPT Portfolio Assistant
        </h1>
        
        {/* Chat Messages */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '8px', 
          padding: '16px', 
          marginBottom: '16px', 
          height: '400px', 
          overflowY: 'auto',
          border: '1px solid #e5e7eb'
        }}>
          {messages.length === 0 ? (
            <div style={{ color: '#6b7280', textAlign: 'center', paddingTop: '150px' }}>
              Ask me anything about your portfolio, risk analysis, or market insights!
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {messages.map((msg, index) => (
                <div key={index} style={{ 
                  display: 'flex', 
                  justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start' 
                }}>
                  <div style={{
                    maxWidth: '70%',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    backgroundColor: msg.sender === 'user' ? '#3b82f6' : '#f3f4f6',
                    color: msg.sender === 'user' ? 'white' : '#374151'
                  }}>
                    {msg.text}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                  <div style={{
                    maxWidth: '70%',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    backgroundColor: '#f3f4f6',
                    color: '#374151'
                  }}>
                    Thinking...
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Chat Input */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '8px', 
          padding: '16px',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask about portfolio analysis, risk metrics, market insights..."
              style={{
                flex: 1,
                minHeight: '80px',
                padding: '12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px',
                resize: 'vertical'
              }}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
            />
            <button
              onClick={handleSendMessage}
              disabled={!message.trim() || isLoading}
              style={{
                padding: '12px 24px',
                backgroundColor: message.trim() && !isLoading ? '#3b82f6' : '#9ca3af',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: message.trim() && !isLoading ? 'pointer' : 'not-allowed',
                alignSelf: 'flex-end'
              }}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
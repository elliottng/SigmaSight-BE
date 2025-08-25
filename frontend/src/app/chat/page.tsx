'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import Image from 'next/image'

interface ChatMessage {
  id: string
  content: string
  sender: 'user' | 'agent'
  timestamp: Date
  status?: 'sending' | 'sent' | 'error'
}

interface AgentStatus {
  online: boolean
  message: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [agentStatus, setAgentStatus] = useState<AgentStatus>({
    online: false,
    message: 'Connecting...'
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const AGENT_URL = 'http://localhost:8787'

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const checkAgentStatus = async () => {
    try {
      const response = await fetch(`${AGENT_URL}/health`)
      if (response.ok) {
        setAgentStatus({
          online: true,
          message: 'Online'
        })
      } else {
        setAgentStatus({
          online: false,
          message: 'Error'
        })
      }
    } catch (error) {
      setAgentStatus({
        online: false,
        message: 'Offline'
      })
    }
  }

  useEffect(() => {
    checkAgentStatus()
    const interval = setInterval(checkAgentStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const sendMessage = async () => {
    if (!input.trim() || !agentStatus.online) return

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      content: input.trim(),
      sender: 'user',
      timestamp: new Date(),
      status: 'sent'
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    try {
      // Try the GPT agent analyze endpoint first
      const response = await fetch(`${AGENT_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          portfolio_id: 'demo-portfolio-id',
          user_context: 'SigmaSight Portfolio Analysis'
        })
      })

      if (response.ok) {
        const data = await response.json()
        const agentMessage: ChatMessage = {
          id: `agent-${Date.now()}`,
          content: data.response || data.analysis || JSON.stringify(data, null, 2),
          sender: 'agent',
          timestamp: new Date(),
          status: 'sent'
        }
        setMessages(prev => [...prev, agentMessage])
      } else {
        // Try alternative chat endpoint if analyze fails
        const chatResponse = await fetch(`${AGENT_URL}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: userMessage.content
          })
        })

        if (chatResponse.ok) {
          const chatData = await chatResponse.json()
          const agentMessage: ChatMessage = {
            id: `agent-${Date.now()}`,
            content: chatData.response || chatData.message || 'Response received',
            sender: 'agent',
            timestamp: new Date(),
            status: 'sent'
          }
          setMessages(prev => [...prev, agentMessage])
        } else {
          throw new Error(`GPT Agent responded with status ${response.status}`)
        }
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: `agent-error-${Date.now()}`,
        content: `Unable to connect to GPT Agent. Please ensure the agent is running on port 8787. Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        sender: 'agent',
        timestamp: new Date(),
        status: 'error'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-white text-gray-800">
      {/* Header */}
      <header className="flex items-center justify-between p-4 lg:px-8 border-b border-gray-200 bg-white">
        <Link href="/" className="flex items-center gap-3 text-gray-800 no-underline">
          <Image 
            src="/assets/sigmasight-logo.png"
            alt="SigmaSight Logo"
            width={32}
            height={32}
            className="w-8 h-8 object-contain"
          />
          <span className="text-xl font-semibold text-gray-800">SigmaSight</span>
        </Link>
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${agentStatus.online ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-600">GPT Agent: {agentStatus.message}</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 flex items-center justify-center mx-auto mb-6">
                <Image 
                  src="/assets/sigmasight-logo.png"
                  alt="SigmaSight Logo"
                  width={64}
                  height={64}
                  className="w-16 h-16 object-contain"
                />
              </div>
              <h2 className="text-3xl font-medium text-gray-800 mb-4">Do you know the risks in your portfolio?</h2>
              <p className="text-lg text-gray-600 max-w-lg mb-8">
                Get AI driven institutional grade portfolio analysis in plain English
              </p>
            </div>
          ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start space-x-3 ${
                  message.sender === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.sender === 'agent' && (
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                    🤖
                  </div>
                )}
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                    message.sender === 'user'
                      ? 'bg-blue-600 text-white rounded-br-sm'
                      : message.status === 'error'
                      ? 'bg-red-50 text-red-800 border border-red-200 rounded-bl-sm'
                      : 'bg-gray-100 text-gray-900 rounded-bl-sm'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <p className="text-xs mt-2 opacity-70">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
                {message.sender === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                    👤
                  </div>
                )}
              </div>
            ))}
            {isTyping && (
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  🤖
                </div>
                <div className="bg-gray-100 px-4 py-3 rounded-lg rounded-bl-sm">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-sm text-gray-500">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
        </div>

        {/* Chat Input */}
        <div className="border-t border-gray-200 p-6 bg-white">
          <div className="max-w-4xl mx-auto">
            <div className="relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="What are my biggest risks? How correlated are my positions?"
                className="w-full resize-none rounded-lg border border-gray-200 px-4 py-3 pr-12 text-gray-800 outline-none focus:border-blue-600 transition-colors min-h-[50px] placeholder-gray-400"
                rows={1}
                disabled={!agentStatus.online || isTyping}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || !agentStatus.online || isTyping}
                className="absolute right-2 bottom-2 p-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
            <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
              <span>Press Enter to send • Shift+Enter for new line</span>
              <span>{agentStatus.online ? 'Connected to GPT Agent' : 'Connecting...'}</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
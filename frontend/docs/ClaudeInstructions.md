Prompt for Claude
'use client'

import { useState } from "react"
import Link from "next/link"

export default function SignupPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    productType: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState('')

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError('')
    
    try {
      const response = await fetch('/api/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        throw new Error('Failed to submit signup')
      }

      const result = await response.json()
      setIsSubmitted(true)
    } catch (err) {
      setError('Something went wrong. Please try again.')
      console.error('Signup error:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-white text-gray-800 flex items-center justify-center p-8">
        <div className="max-w-md w-full text-center">
          <div className="mb-8">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-2xl font-semibold text-gray-800 mb-2">You're on the waitlist!</h1>
            <p className="text-gray-600 mb-6">
              Thank you for signing up. We'll notify you as soon as SigmaSight is ready for the {formData.productType} tier.
            </p>
            <Link 
              href="/"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-all no-underline"
            >
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white text-gray-800">
      {/* Header */}
      <header className="flex items-center justify-between p-4 lg:px-8 border-b border-gray-200 bg-white">
        <Link href="/" className="flex items-center gap-2 text-gray-800 no-underline">
          <div className="w-8 h-8 flex items-center justify-center">
            <svg viewBox="0 0 100 100" className="w-8 h-8">
              <defs>
                <linearGradient id="dotGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#1e40af" stopOpacity={1} />
                  <stop offset="100%" stopColor="#2563eb" stopOpacity={1} />
                </linearGradient>
              </defs>
              <g transform="translate(50,50)">
                <circle cx="0" cy="0" r="3" fill="url(#dotGradient)" />
                <circle cx="-6" cy="0" r="3" fill="url(#dotGradient)" />
                <circle cx="6" cy="0" r="3" fill="url(#dotGradient)" />
                <circle cx="-12" cy="0" r="2.5" fill="url(#dotGradient)" />
                <circle cx="12" cy="0" r="2.5" fill="url(#dotGradient)" />
                <circle cx="-18" cy="0" r="2" fill="url(#dotGradient)" />
                <circle cx="18" cy="0" r="2" fill="url(#dotGradient)" />
                <circle cx="-24" cy="0" r="1.5" fill="url(#dotGradient)" />
                <circle cx="24" cy="0" r="1.5" fill="url(#dotGradient)" />
                <circle cx="-30" cy="0" r="1" fill="url(#dotGradient)" />
                <circle cx="30" cy="0" r="1" fill="url(#dotGradient)" />
                <circle cx="0" cy="-6" r="3" fill="url(#dotGradient)" />
                <circle cx="0" cy="6" r="3" fill="url(#dotGradient)" />
                <circle cx="-6" cy="-6" r="2.5" fill="url(#dotGradient)" />
                <circle cx="6" cy="-6" r="2.5" fill="url(#dotGradient)" />
                <circle cx="-6" cy="6" r="2.5" fill="url(#dotGradient)" />
                <circle cx="6" cy="6" r="2.5" fill="url(#dotGradient)" />
                <circle cx="-12" cy="-6" r="2" fill="url(#dotGradient)" />
                <circle cx="12" cy="-6" r="2" fill="url(#dotGradient)" />
                <circle cx="-12" cy="6" r="2" fill="url(#dotGradient)" />
                <circle cx="12" cy="6" r="2" fill="url(#dotGradient)" />
              </g>
            </svg>
          </div>
          <span className="text-xl font-semibold text-gray-800">SigmaSight</span>
        </Link>
      </header>

      {/* Main Content */}
      <main className="flex items-center justify-center min-h-[calc(100vh-80px)] p-8">
        <div className="max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-normal text-gray-800 mb-4">
              SigmaSight is in beta
            </h1>
            <p className="text-lg text-gray-600">
              To be added to our waitlist, please sign up below
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <input
                type="text"
                id="name"
                name="name"
                required
                value={formData.name}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-200 rounded-lg text-gray-800 outline-none focus:border-blue-600 transition-colors"
                placeholder="Enter your full name"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                id="email"
                name="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-200 rounded-lg text-gray-800 outline-none focus:border-blue-600 transition-colors"
                placeholder="Enter your email address"
              />
            </div>

            <div>
              <label htmlFor="productType" className="block text-sm font-medium text-gray-700 mb-2">
                Product Tier
              </label>
              <select
                id="productType"
                name="productType"
                required
                value={formData.productType}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-200 rounded-lg text-gray-800 outline-none focus:border-blue-600 transition-colors bg-white"
              >
                <option value="">Select a product tier</option>
                <option value="Basic">Basic - Simple Portfolios (Free)</option>
                <option value="Standard">Standard - Multi-Asset Portfolios ($9/month)</option>
                <option value="Professional">Professional - Advanced Strategies ($29/month)</option>
              </select>
            </div>

            {error && (
              <div className="text-red-600 text-sm text-center">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isSubmitting ? 'Joining Waitlist...' : 'Join Waitlist'}
            </button>
          </form>

          <div className="text-center mt-6">
            <Link 
              href="/"
              className="text-sm text-gray-600 hover:text-gray-800 no-underline"
            >
              ← Back to home
            </Link>
          </div>
        </div>
      </main>
    </div>
  )
}

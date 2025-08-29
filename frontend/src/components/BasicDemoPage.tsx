"use client"

import React from 'react'

export function BasicDemoPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-2xl font-bold text-primary">
                SigmaSight
              </div>
              <nav className="hidden md:flex items-center space-x-6">
                <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                  Portfolio
                </a>
                <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                  Analytics
                </a>
                <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                  Risk
                </a>
                <a href="#" className="text-muted-foreground hover:text-foreground transition-colors">
                  Reports
                </a>
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <button className="px-4 py-2 text-sm bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors">
                Sign In
              </button>
              <button className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">
                Get Started
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 text-foreground">
            Advanced Portfolio
            <span className="text-primary"> Risk Analytics</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
            Comprehensive risk management and portfolio analytics platform designed for
            institutional investors and financial professionals.
          </p>
          <div className="flex justify-center space-x-4">
            <button className="px-8 py-4 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-semibold">
              Start Free Trial
            </button>
            <button className="px-8 py-4 border border-border text-foreground rounded-lg hover:bg-accent hover:text-accent-foreground transition-colors font-semibold">
              View Demo
            </button>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-16 px-4 bg-muted/50">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-foreground">
            Powerful Analytics Tools
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 bg-card border border-border rounded-lg">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <div className="w-6 h-6 bg-primary rounded"></div>
              </div>
              <h3 className="text-xl font-semibold mb-3 text-card-foreground">Risk Metrics</h3>
              <p className="text-muted-foreground">
                Comprehensive risk analysis with VaR, CVaR, and advanced stress testing capabilities.
              </p>
            </div>
            <div className="p-6 bg-card border border-border rounded-lg">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <div className="w-6 h-6 bg-primary rounded"></div>
              </div>
              <h3 className="text-xl font-semibold mb-3 text-card-foreground">Portfolio Analytics</h3>
              <p className="text-muted-foreground">
                Deep portfolio analysis with performance attribution and factor exposure insights.
              </p>
            </div>
            <div className="p-6 bg-card border border-border rounded-lg">
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                <div className="w-6 h-6 bg-primary rounded"></div>
              </div>
              <h3 className="text-xl font-semibold mb-3 text-card-foreground">Real-time Monitoring</h3>
              <p className="text-muted-foreground">
                Live market data integration with automated alerts and risk threshold monitoring.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Dashboard Preview */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-foreground">
            Intuitive Dashboard
          </h2>
          <div className="bg-card border border-border rounded-xl p-8 shadow-lg">
            <div className="space-y-6">
              {/* Mock Dashboard Header */}
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold text-card-foreground">Portfolio Overview</h3>
                <div className="flex space-x-2">
                  <div className="px-3 py-1 bg-primary/10 text-primary text-sm rounded">
                    Total Value: $2.4M
                  </div>
                  <div className="px-3 py-1 bg-accent/10 text-accent-foreground text-sm rounded">
                    Daily P&L: +$12.5K
                  </div>
                </div>
              </div>
              
              {/* Mock Chart Area */}
              <div className="h-64 bg-muted/50 rounded-lg flex items-center justify-center">
                <div className="text-muted-foreground">
                  Interactive Portfolio Performance Chart
                </div>
              </div>
              
              {/* Mock Metrics Grid */}
              <div className="grid md:grid-cols-4 gap-4">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="text-sm text-muted-foreground">Value at Risk</div>
                  <div className="text-xl font-bold text-foreground">$45.2K</div>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="text-sm text-muted-foreground">Sharpe Ratio</div>
                  <div className="text-xl font-bold text-foreground">1.47</div>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="text-sm text-muted-foreground">Max Drawdown</div>
                  <div className="text-xl font-bold text-foreground">-8.4%</div>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <div className="text-sm text-muted-foreground">Beta</div>
                  <div className="text-xl font-bold text-foreground">0.92</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 bg-card border-t border-border">
        <div className="container mx-auto">
          <div className="flex justify-between items-center">
            <div className="text-xl font-bold text-primary">
              SigmaSight
            </div>
            <div className="text-sm text-muted-foreground">
              © 2024 SigmaSight. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
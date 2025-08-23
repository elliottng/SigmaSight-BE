# SigmaSight React UI Development Instructions for Windsurf/Claude

## Project Overview

Build a comprehensive React application (mobile and desktop responsive) that connects the SigmaSight backend API (`elliottng/sigmasight-be`) with the SigmaSight-v5 functionality, using the design aesthetic from the `bbalbale/SigmaSight-landing-pages-p7` repository.

## Quick Start for Windsurf

**Ask Claude in Windsurf:**
```
"Please help me set up a new Next.js project using these SigmaSight UI instructions. Start with the project structure and basic layout components."
```

**Or for specific components:**
```
"Based on these instructions, please create the Dashboard component with the metric cards and API integration."
```

## Architecture & Tech Stack

### Core Technologies
- **Framework**: Next.js 15.2.4 with App Router
- **UI Library**: React 18+ with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **State Management**: React hooks (useState, useReducer, useContext)
- **API Integration**: Native fetch with async/await
- **Charts/Visualization**: Recharts library
- **Icons**: Lucide React
- **Responsive**: Mobile-first design with desktop enhancement

### Design System (from landing-pages-p7)
```typescript
// Design tokens to implement
const designSystem = {
  colors: {
    background: '#0A0A0A',      // Dark theme primary
    surface: '#1A1A1A',        // Card backgrounds
    border: '#2A2A2A',         // Subtle borders
    text: {
      primary: '#FFFFFF',      // Primary text
      secondary: '#9CA3AF',    // Secondary text
      muted: '#6B7280'         // Muted text
    },
    accent: '#3B82F6',         // Blue accent
    status: {
      success: '#10B981',      // Green
      warning: '#F59E0B',      // Yellow
      danger: '#EF4444',       // Red
      info: '#3B82F6'          // Blue
    }
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem', 
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    xxl: '3rem'
  },
  animation: {
    transition: '150ms ease-in-out',
    hover: 'transform 0.2s ease',
    loading: 'pulse 2s infinite'
  }
}
```

## Application Structure

### Main Navigation Tabs
1. **Dashboard (Home)** - Portfolio overview and key metrics
2. **Positions** - Detailed position management
3. **Risk Analytics** - Risk metrics and factor analysis  
4. **Performance** - Historical performance tracking
5. **Reports** - Generated portfolio reports viewer

### Responsive Layout Pattern
```typescript
// Layout structure to implement
const Layout = () => (
  <div className="min-h-screen bg-[#0A0A0A] text-white">
    {/* Header - Desktop */}
    <header className="hidden md:flex items-center justify-between p-4 border-b border-[#2A2A2A]">
      <Logo />
      <UserProfile />
    </header>
    
    {/* Main Content */}
    <main className="flex-1 overflow-y-auto pb-16 md:pb-0">
      {renderActiveTab()}
    </main>
    
    {/* Bottom Navigation - Mobile */}
    <nav className="fixed bottom-0 left-0 right-0 md:hidden">
      <TabNavigation />
    </nav>
  </div>
)
```

## Core Features Implementation

### 1. Dashboard Component

```typescript
// Key metrics to display from API
const DashboardMetrics = {
  exposures: {
    longExposure: number,      // From portfolio snapshots
    shortExposure: number,
    grossExposure: number,
    netExposure: number,
    totalPL: number
  },
  displayModes: ['notional', 'deltaAdjusted'],
  timePeriods: ['day', 'week', 'month', 'ytd']
}

// API endpoint mapping
const API_ENDPOINTS = {
  portfolio: '/api/v1/portfolios/{id}',
  exposures: '/api/v1/portfolios/{id}/exposures',
  positions: '/api/v1/portfolios/{id}/positions',
  greeks: '/api/v1/portfolios/{id}/greeks',
  factors: '/api/v1/portfolios/{id}/factor-exposures',
  reports: '/api/v1/reports/{portfolio_id}'
}
```

**Dashboard Cards Layout:**
- 2x2 grid on mobile, 4x1 on desktop
- Each card shows: value, percentage bar, trend indicator
- Color coding based on thresholds
- Interactive period selection
- Real-time updates (simulated)

### 2. Positions Management

**Position Types Support:**
- LONG/SHORT - Equity positions  
- LC/LP/SC/SP - Options positions
- Tags and strategy grouping
- Expandable rows with price charts

**Display Modes:**
- Individual: Each position separate row
- By Type: Grouped by position type
- By Strategy: Grouped by strategy tags

**Position Table Columns:**
```typescript
interface PositionTableRow {
  ticker: string;
  type: 'LONG' | 'SHORT' | 'LC' | 'LP' | 'SC' | 'SP';
  tags: string[];
  quantity: number;
  notionalExposure: number;
  deltaAdjustedExposure: number;
  pnl: number;
  expiryDate?: string;
  greeks: {
    delta?: number;
    gamma?: number;
    theta?: number;
    vega?: number;
    rho?: number;
  };
}
```

### 3. Risk Analytics Dashboard

**Key Sections:**
- Portfolio-level Greeks aggregation
- Factor exposure analysis (8 factors)
- Correlation matrices visualization  
- Stress test results display
- Risk metrics over time

**Charts to Implement:**
- Exposure breakdown (pie/donut charts)
- Greeks over time (line charts)
- Factor exposure heatmap
- Correlation matrices
- Stress test scenario results

### 4. Reports Viewer

**Report Integration:**
```typescript
// Connect to backend report generator
const ReportViewer = {
  formats: ['md', 'json', 'csv'],
  apiEndpoint: '/api/v1/reports/generate',
  displayModes: {
    markdown: 'Human-readable view',
    json: 'Structured data view', 
    csv: 'Tabular Excel-like view'
  }
}
```

**Report Features:**
- Auto-generate daily reports
- Historical report access
- Export functionality
- Real-time regeneration
- Share/email capabilities

## API Integration Strategy

### Authentication Flow
```typescript
// JWT-based authentication
const AuthContext = {
  login: async (email: string, password: string) => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const { access_token } = await response.json();
    localStorage.setItem('auth_token', access_token);
    return access_token;
  },
  
  // Demo accounts for testing:
  demoAccounts: [
    { email: 'demo_individual@sigmasight.com', password: 'demo12345' },
    { email: 'demo_hnw@sigmasight.com', password: 'demo12345' },
    { email: 'demo_hedgefundstyle@sigmasight.com', password: 'demo12345' }
  ]
}
```

### Data Fetching Patterns
```typescript
// Unified API client
const apiClient = {
  get: async (endpoint: string) => {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  },
  
  // Automatic retry logic
  // Error handling
  // Loading states management
}
```

### Real-time Updates Simulation
```typescript
// Simulate real-time data updates
const useRealTimeData = (endpoint: string, interval: number = 30000) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await apiClient.get(endpoint);
        setData(result);
        setLoading(false);
      } catch (error) {
        console.error('API Error:', error);
      }
    };
    
    fetchData();
    const intervalId = setInterval(fetchData, interval);
    return () => clearInterval(intervalId);
  }, [endpoint, interval]);
  
  return { data, loading };
};
```

## Interactive Components

### 1. Metric Cards with Animations
```typescript
const MetricCard = ({ title, value, trend, threshold }) => (
  <div className="bg-[#1A1A1A] border border-[#2A2A2A] rounded-lg p-4 hover:border-[#3B82F6] transition-all">
    <h3 className="text-sm text-[#9CA3AF] mb-2">{title}</h3>
    <div className="flex items-center justify-between">
      <span className="text-2xl font-bold">{formatCurrency(value)}</span>
      <TrendIndicator trend={trend} />
    </div>
    <ProgressBar value={value} threshold={threshold} />
  </div>
)
```

### 2. Expandable Position Rows
```typescript
const PositionRow = ({ position, expanded, onToggle }) => (
  <tr className="border-b border-[#2A2A2A] hover:bg-[#1A1A1A]">
    <td className="p-3">
      <button onClick={onToggle} className="flex items-center gap-2">
        <ChevronRight className={`w-4 h-4 transition-transform ${expanded ? 'rotate-90' : ''}`} />
        {position.ticker}
      </button>
      {expanded && <MiniChart ticker={position.ticker} />}
    </td>
    {/* Additional columns */}
  </tr>
)
```

### 3. Filter and Search Components
```typescript
const PositionFilters = ({ onFilterChange }) => (
  <div className="flex flex-wrap gap-2 mb-4">
    <SearchInput placeholder="Search positions..." />
    <FilterChips options={['All', 'LONG', 'SHORT', 'Options']} />
    <SortDropdown options={['Ticker', 'P&L', 'Exposure']} />
  </div>
)
```

## Performance Optimizations

### 1. Virtual Scrolling for Large Lists
```typescript
// For portfolios with 100+ positions
const VirtualizedPositionTable = ({ positions }) => {
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 50 });
  
  // Implement virtual scrolling logic
  // Only render visible rows
  // Maintain scroll position
}
```

### 2. Data Caching Strategy
```typescript
// Cache frequently accessed data
const useDataCache = () => {
  const cache = useRef(new Map());
  
  const getCachedData = (key: string, fetcher: Function, ttl: number = 300000) => {
    const cached = cache.current.get(key);
    if (cached && Date.now() - cached.timestamp < ttl) {
      return cached.data;
    }
    
    // Fetch fresh data
    fetcher().then(data => {
      cache.current.set(key, { data, timestamp: Date.now() });
    });
  };
}
```

### 3. Optimistic UI Updates
```typescript
// Show immediate feedback while API calls complete
const useOptimisticUpdates = () => {
  const [localState, setLocalState] = useState();
  const [serverState, setServerState] = useState();
  
  const updateOptimistically = (newValue, apiCall) => {
    setLocalState(newValue); // Immediate UI update
    apiCall()
      .then(result => setServerState(result))
      .catch(() => setLocalState(serverState)); // Revert on error
  };
}
```

## Error Handling & Loading States

### 1. Comprehensive Error Boundaries
```typescript
const ErrorBoundary = ({ children, fallback }) => {
  // Handle JavaScript errors
  // Show user-friendly error messages
  // Log errors for debugging
  // Provide retry mechanisms
}
```

### 2. Loading State Management
```typescript
const LoadingStates = {
  skeleton: <SkeletonLoader />,        // For initial loads
  spinner: <SpinnerLoader />,         // For quick updates  
  progress: <ProgressLoader />,       // For file operations
  inline: <InlineLoader />            // For inline updates
}
```

### 3. Offline Support
```typescript
// Handle connectivity issues
const useOfflineSupport = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  
  // Cache critical data locally
  // Show offline indicators
  // Queue actions for when online
  // Sync when connection restored
}
```

## Testing Strategy

### 1. Component Testing
```typescript
// Test each component in isolation
describe('MetricCard', () => {
  it('displays currency values correctly', () => {
    render(<MetricCard value={1500000} />);
    expect(screen.getByText('$1,500,000')).toBeInTheDocument();
  });
  
  it('shows correct trend indicators', () => {
    // Test trend calculation and display
  });
});
```

### 2. API Integration Testing
```typescript
// Mock API responses for development
const mockApiData = {
  portfolio: { /* demo portfolio data */ },
  positions: [ /* demo positions */ ],
  reports: { /* sample reports */ }
}
```

### 3. User Flow Testing
```typescript
// Test complete user workflows
describe('Portfolio Dashboard Flow', () => {
  it('loads dashboard data and navigates to positions', async () => {
    // Simulate user interaction
    // Verify data loads correctly
    // Test navigation between sections
  });
});
```

## Deployment Configuration

### 1. Environment Variables
```typescript
// Configure for different environments
const config = {
  API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000',
  AUTH_ENABLED: process.env.NEXT_PUBLIC_AUTH_ENABLED === 'true',
  DEMO_MODE: process.env.NEXT_PUBLIC_DEMO_MODE === 'true'
}
```

### 2. Build Optimizations
```typescript
// Next.js configuration
const nextConfig = {
  images: { domains: ['assets.sigmasight.com'] },
  compress: true,
  poweredByHeader: false,
  generateEtags: false,
  experimental: {
    optimizeCss: true,
    optimizeImages: true
  }
}
```

## Development Workflow

### 1. Component Development Order
1. Layout and navigation structure
2. Authentication flow and demo accounts
3. Dashboard with metric cards
4. Positions table with filtering
5. Risk analytics visualizations  
6. Reports viewer integration
7. Mobile responsiveness refinement
8. Performance optimizations
9. Error handling and edge cases
10. Testing and documentation

### 2. API Integration Steps
1. Set up mock API responses for development
2. Implement authentication with demo accounts
3. Connect portfolio data endpoints
4. Integrate position management
5. Add real-time data updates
6. Connect report generation
7. Handle error states and loading
8. Add offline support
9. Performance monitoring
10. Production deployment

### 3. Design Implementation Priority
1. Core layout structure (dark theme)
2. Typography and spacing system
3. Interactive components (buttons, forms)
4. Data visualization components
5. Animation and micro-interactions
6. Responsive breakpoints
7. Accessibility improvements
8. Cross-browser testing
9. Performance audits
10. User experience refinement

This comprehensive guide provides the foundation for building a production-ready SigmaSight React application that seamlessly integrates the backend functionality with an intuitive, responsive user interface matching the established design aesthetic.
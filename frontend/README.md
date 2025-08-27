# SigmaSight Frontend

A modern, responsive React/Next.js frontend application for the SigmaSight portfolio risk management platform.

## 🚀 Features

### Core Functionality
- **Authentication System** - JWT-based login/register with session management
- **Portfolio Dashboard** - Real-time portfolio overview with key metrics
- **Position Management** - Comprehensive position listing, editing, and analysis
- **Risk Analytics** - Options Greeks and factor exposure analysis
- **Market Data** - Real-time quotes and market information
- **Report Generation** - Professional PDF/CSV/JSON report creation

### Technical Features
- **Responsive Design** - Mobile-first approach with desktop optimization
- **Real-time Data** - Live market data and portfolio updates
- **Error Handling** - Comprehensive error boundaries and user feedback
- **Loading States** - Smooth loading experiences throughout
- **Type Safety** - Full TypeScript implementation
- **Modern UI** - Clean, professional interface with Tailwind CSS

## 🛠️ Tech Stack

- **Framework**: Next.js 15 with React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios with interceptors
- **State Management**: React Context + Hooks
- **Icons**: Lucide React
- **Forms**: React Hook Form with Zod validation
- **Charts**: Recharts for data visualization
- **Tables**: TanStack Table for advanced data grids

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js app router pages
│   │   ├── dashboard/       # Dashboard page
│   │   ├── positions/       # Positions management
│   │   ├── risk/           # Risk analytics
│   │   ├── market/         # Market data
│   │   ├── reports/        # Report generation
│   │   ├── login/          # Authentication
│   │   └── register/       # User registration
│   ├── components/         # Reusable components
│   │   ├── ui/            # Base UI components
│   │   ├── layout/        # Layout components
│   │   ├── auth/          # Authentication components
│   │   ├── dashboard/     # Dashboard-specific
│   │   ├── positions/     # Position-specific
│   │   ├── risk/          # Risk analytics
│   │   └── market/        # Market data
│   ├── contexts/          # React contexts
│   ├── services/          # API services
│   ├── lib/              # Utilities and types
│   └── styles/           # Global styles
├── public/               # Static assets
└── docs/                # Documentation
```

## 🎨 Component Architecture

### UI Components
- **Button** - Configurable button with variants and loading states
- **Input** - Form input with error handling
- **Card** - Flexible card layout component
- **MetricCard** - Specialized card for displaying metrics
- **LoadingSpinner** - Various loading indicators
- **ErrorDisplay** - Error handling components
- **EmptyState** - Empty state placeholders

### Layout Components
- **Navigation** - Responsive sidebar navigation
- **DashboardLayout** - Main application layout
- **ProtectedRoute** - Authentication guard

### Feature Components
- **PortfolioOverview** - Portfolio summary and metrics
- **PositionTable** - Advanced position data grid
- **GreeksDisplay** - Options Greeks visualization
- **FactorExposure** - Risk factor analysis
- **QuoteTable** - Real-time market quotes
- **AlertsPanel** - Risk alerts and notifications

## 🔧 Configuration

### Environment Variables
Create a `.env.local` file in the frontend directory:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws

# App Configuration
NEXT_PUBLIC_APP_NAME=SigmaSight
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### API Configuration
The application is configured to work with the SigmaSight backend API:

- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://api.sigmasight.com/v1`

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- SigmaSight backend running on port 8000

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Build for production**
   ```bash
   npm run build
   npm start
   ```

### Demo Accounts
Use these credentials to test the application:

- **Individual Investor**: `demo_individual@sigmasight.com` / `demo123`
- **High Net Worth**: `demo_hnw@sigmasight.com` / `demo123`  
- **Hedge Fund Style**: `demo_hedgefundstyle@sigmasight.com` / `demo123`

## 📱 Responsive Design

The application is fully responsive with breakpoints:

- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

### Mobile Features
- Touch-friendly interface
- Collapsible navigation
- Optimized table layouts
- Swipe gestures where appropriate

## 🔐 Security

### Authentication
- JWT token-based authentication
- Automatic token refresh
- Secure token storage
- Protected route guards

### Data Security
- Input validation and sanitization
- XSS protection
- CSRF protection via API design
- Secure HTTP headers

## 📊 Data Management

### API Integration
- RESTful API client with interceptors
- Automatic error handling
- Request/response logging
- Rate limiting awareness

### State Management
- React Context for global state
- Local component state for UI
- Optimistic updates where appropriate
- Caching strategies for performance

## 🧪 Testing

### Testing Strategy
- Unit tests for utilities and helpers
- Component testing with React Testing Library
- Integration tests for API services
- E2E tests for critical user flows

### Running Tests
```bash
# Unit and component tests
npm test

# E2E tests
npm run test:e2e

# Coverage report
npm run test:coverage
```

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Docker Deployment
```bash
# Build Docker image
docker build -t sigmasight-frontend .

# Run container
docker run -p 3000:3000 sigmasight-frontend
```

### Environment-Specific Builds
- **Development**: Hot reloading, debug tools
- **Staging**: Production optimizations, staging API
- **Production**: Full optimizations, CDN assets

## 📈 Performance

### Optimization Features
- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js Image component
- **Bundle Analysis**: Webpack bundle analyzer
- **Caching**: Aggressive caching strategies
- **Compression**: Gzip/Brotli compression

### Performance Metrics
- First Contentful Paint < 2s
- Time to Interactive < 3s
- Cumulative Layout Shift < 0.1
- Lighthouse Score > 90

## 🎯 Browser Support

### Supported Browsers
- Chrome 90+
- Firefox 90+
- Safari 14+
- Edge 90+

### Progressive Enhancement
- Core functionality works without JavaScript
- Enhanced features with JavaScript enabled
- Fallbacks for unsupported features

## 🤝 Contributing

### Development Workflow
1. Create feature branch from `main`
2. Implement changes with tests
3. Submit pull request
4. Code review and approval
5. Merge to main

### Code Standards
- TypeScript strict mode
- ESLint + Prettier formatting
- Conventional commit messages
- Component documentation

## 📚 Additional Resources

### Documentation
- [Component Storybook](./docs/storybook.md)
- [API Integration Guide](./docs/api-integration.md)
- [Deployment Guide](./docs/deployment.md)
- [Contributing Guidelines](./docs/contributing.md)

### External Dependencies
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)

## 📄 License

This project is part of the SigmaSight portfolio risk management platform.

---

For questions or support, contact the development team or refer to the project documentation.
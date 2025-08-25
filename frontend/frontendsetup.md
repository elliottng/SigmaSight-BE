# SigmaSight Frontend Setup Guide

This guide provides step-by-step instructions to get the SigmaSight frontend server running with the GPT Agent chat interface.

## Prerequisites

- Node.js (v18+ recommended)
- npm or yarn package manager
- Backend server running on port 8000
- GPT Agent server running on port 8787

## Quick Start

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Access the application:**
   - Main interface: http://localhost:3000 (or next available port)
   - Chat interface: http://localhost:3000/chat

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── chat/
│   │   │   └── page.tsx        # Main chat interface
│   │   ├── globals.css         # Global styles with CSS variables
│   │   ├── layout.tsx          # Root layout component
│   │   └── page.tsx           # Homepage (redirects to chat)
│   └── assets/
│       └── SigmaSight Logo.png # Original logo file
├── public/
│   └── assets/
│       └── sigmasight-logo.png # Web-optimized logo
├── package.json                # Dependencies and scripts
├── tailwind.config.js         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
└── next.config.js             # Next.js configuration
```

## Configuration Files

### Environment Variables (.env)
The frontend uses the same .env file as the backend:
```env
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
# ... other backend variables
```

### Tailwind Configuration
Custom CSS variables are defined in `src/app/globals.css` for theming:
- Light/dark mode support
- SigmaSight color scheme
- Responsive design utilities

## Features

### Chat Interface
- **Real-time GPT Agent connectivity** on port 8787
- **Agent status monitoring** with visual indicators
- **Professional messaging interface** similar to Claude AI/OpenAI
- **SigmaSight branding** with custom logo integration

### Technical Features
- **Next.js 15** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Responsive design** for mobile/desktop
- **Error handling** for agent connectivity issues

## GPT Agent Integration

The chat interface connects to your GPT Agent with these endpoints:

1. **Primary endpoint:** `POST /analyze`
   ```json
   {
     "message": "user message",
     "portfolio_id": "demo-portfolio-id",
     "user_context": "SigmaSight Portfolio Analysis"
   }
   ```

2. **Fallback endpoint:** `POST /chat`
   ```json
   {
     "message": "user message"
   }
   ```

3. **Health check:** `GET /health`

## Troubleshooting

### Common Issues

#### 1. Internal Server Error (500)
**Solution:** Clear Next.js build cache
```bash
rm -rf .next
npm run dev
```

#### 2. Port Already in Use
**Solution:** Next.js will automatically use the next available port (3001, 3002, etc.)

#### 3. GPT Agent Connection Issues
- Ensure GPT Agent server is running on port 8787
- Check the agent status indicator in the chat header
- Verify backend server is running on port 8000

#### 4. Logo Not Displaying
- Ensure `public/assets/sigmasight-logo.png` exists
- Check browser console for 404 errors
- Verify Next.js Image component imports

#### 5. Styling Issues
- Clear browser cache
- Restart development server
- Check Tailwind CSS compilation in terminal

### Development Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type checking
npm run type-check

# Linting (if configured)
npm run lint
```

## Deployment Notes

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Static assets:** Logo files must be in the `public/` directory for production

3. **Environment variables:** Ensure production environment variables are properly configured

4. **GPT Agent endpoints:** Update AGENT_URL for production environment

## Development Workflow

1. **Start backend server** (port 8000)
2. **Start GPT Agent server** (port 8787)
3. **Start frontend development server** (port 3000+)
4. **Access chat interface** and test GPT Agent connectivity
5. **Monitor agent status** via header indicator

## Support

If you encounter issues:
1. Check the browser console for JavaScript errors
2. Check the terminal for build/compilation errors
3. Verify all servers (backend, GPT agent, frontend) are running
4. Clear build cache and restart if needed

---

*Last updated: Based on current Next.js 15 setup with GPT Agent integration*
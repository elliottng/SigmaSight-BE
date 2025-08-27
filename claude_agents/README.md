# SigmaSight Claude Agents Configuration

## Overview
This directory contains specialized Claude agent configurations for different aspects of SigmaSight development. Each agent is optimized for specific tasks while maintaining consistency with the project architecture.

## Available Agents

### 1. Database Agent 🗄️ (`database_agent.md`)
**Expert in:** Database schema, API endpoints, SQLAlchemy models
- Database design and migrations
- FastAPI endpoint development
- Async database patterns
- Query optimization

### 2. Frontend Agent ⚛️ (`frontend_agent.md`)
**Expert in:** React/Next.js development, UI components
- Component development
- Backend integration
- State management
- Responsive design

### 3. Testing Agent 🧪 (`testing_agent.md`)
**Expert in:** Testing, quality assurance, code review
- Unit and integration testing
- Code review
- Performance testing
- Error handling validation

### 4. Documentation Agent 📝 (`documentation_agent.md`)
**Expert in:** Technical documentation, API docs, guides
- API documentation
- Technical guides
- Architecture documentation
- Troubleshooting guides

### 5. Performance Agent ⚡ (`performance_agent.md`)
**Expert in:** Performance optimization, caching, scalability
- Database optimization
- Caching strategies
- Memory optimization
- Performance monitoring

### 6. GPT Analysis Agent 🤖 (`gpt_analysis_agent.md`)
**Expert in:** Financial analysis, portfolio optimization
- Portfolio risk analysis
- Financial data interpretation
- Analysis script optimization
- Cross-agent collaboration

## How to Use These Agents

### Method 1: Copy-Paste Configuration
1. Choose the appropriate agent for your task
2. Open the corresponding `.md` file
3. Copy the "Custom Instructions" section
4. Paste into a new Claude conversation
5. Start working on your specific task

### Method 2: Reference During Development
1. Keep the relevant agent configuration open while working
2. Follow the patterns and guidelines specified
3. Use the essential commands provided
4. Reference the focus areas for task prioritization

## Agent Coordination

### Workflow Pattern:
```
Database Agent → Creates APIs → Frontend Agent uses them
       ↓
Testing Agent validates → Documentation Agent documents
       ↓
Performance Agent optimizes
       ↓
GPT Analysis Agent analyzes results
```

### Shared Responsibilities:
- All agents update `backend/AI_AGENT_REFERENCE.md` with discoveries
- Use existing demo data (3 portfolios, 63 positions)
- Follow async patterns consistently
- Maintain documentation standards

## Essential Setup Commands (All Agents)

```bash
# Start database
docker-compose up -d

# Apply migrations
uv run alembic upgrade head

# Seed demo data
python backend/scripts/reset_and_seed.py seed

# Verify setup
uv run python -c "from app.models.users import Portfolio; print('✅ Models working')"

# Check database content
uv run python backend/scripts/check_database_content.py
```

## Project Structure Quick Reference

```
SigmaSight/
├── backend/                 # FastAPI backend (main focus)
│   ├── app/                 # Application code
│   ├── scripts/             # Utility scripts
│   ├── tests/               # Test suite
│   └── AI_AGENT_REFERENCE.md # Master reference (READ FIRST)
├── frontend/                # Next.js frontend
├── gptagent/               # GPT integration service
└── claude_agents/          # This directory (agent configs)
```

## Success Metrics

### Per Agent:
- **Database**: APIs functional, proper async patterns, optimized queries
- **Frontend**: Components working, error handling, responsive design
- **Testing**: Comprehensive coverage, all tests passing, quality maintained
- **Documentation**: Complete docs, clear guides, current references
- **Performance**: Target response times, optimized queries, efficient processing
- **Analysis**: Accurate insights, optimized scripts, effective collaboration

### Overall Project:
- Consistent use of demo data across all agents
- Current and comprehensive documentation
- Performance targets met
- High code quality maintained
- Effective inter-agent collaboration

## Quick Start

1. **Choose your agent** based on the task at hand
2. **Read the configuration** in the corresponding `.md` file
3. **Start a new Claude conversation** with those instructions
4. **Begin working** following the patterns and guidelines provided
5. **Update documentation** with any new patterns discovered

## Notes

- Always work from the appropriate directory (`backend/` for most tasks)
- Read `backend/AI_AGENT_REFERENCE.md` first for context
- Use existing demo data for testing
- Follow async patterns consistently
- Update documentation with discoveries
- Coordinate with other agents as needed
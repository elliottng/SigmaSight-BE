# Quick Start Guide for SigmaSight Claude Agents

## Immediate Setup (5 minutes)

### Step 1: Choose Your Agent
Pick the agent that matches your current task:
- 🗄️ **Database work** → `database_agent.md`
- ⚛️ **Frontend development** → `frontend_agent.md`
- 🧪 **Testing/QA** → `testing_agent.md`
- 📝 **Documentation** → `documentation_agent.md`
- ⚡ **Performance optimization** → `performance_agent.md`
- 🤖 **Financial analysis** → `gpt_analysis_agent.md`

### Step 2: Start New Claude Conversation
1. Open a new Claude conversation
2. Copy the "Custom Instructions" section from your chosen agent file
3. Paste as the first message
4. Claude is now configured as that specialized agent!

### Step 3: Verify Setup
Ask Claude to run this verification:
```bash
# Verify critical imports work
uv run python -c "from app.models.users import Portfolio; print('✅ Models working')"
```

## Example Agent Activation

### For Database Work:
```
[Paste database_agent.md Custom Instructions]

Hi! I need to add a new API endpoint for portfolio statistics. Can you help me design this following the existing patterns?
```

### For Frontend Work:
```
[Paste frontend_agent.md Custom Instructions]

I need to create a React component that displays portfolio risk metrics with proper loading states. Can you help?
```

## Common First Tasks by Agent

### Database Agent First Tasks:
- Add new API endpoints
- Optimize database queries
- Fix async/sync issues
- Create new data models

### Frontend Agent First Tasks:
- Build React components
- Integrate with backend APIs
- Implement responsive design
- Add error boundaries

### Testing Agent First Tasks:
- Write unit tests for new features
- Review code for async patterns
- Test error handling
- Validate performance

### Documentation Agent First Tasks:
- Update API documentation
- Create troubleshooting guides
- Document new patterns
- Update reference materials

### Performance Agent First Tasks:
- Profile slow operations
- Implement caching
- Optimize database queries
- Monitor memory usage

### Analysis Agent First Tasks:
- Analyze portfolio performance
- Optimize calculation scripts
- Generate financial insights
- Coordinate data requirements

## Essential Knowledge for All Agents

### Project Context:
- **Current Phase**: Portfolio Report Generator (Phase 2.0)
- **Demo Data**: 3 portfolios, 63 positions ready for testing
- **Architecture**: FastAPI backend + Next.js frontend + PostgreSQL
- **Status**: 8 calculation engines, some with data limitations

### Must-Read Files:
1. `backend/AI_AGENT_REFERENCE.md` (master reference)
2. `backend/TODO1.md` (completed work)
3. `backend/TODO2.md` (current tasks)

### Working Directory:
- Most work: `backend/` directory
- Frontend work: `frontend/` directory
- Always use `uv run` for Python commands

## Troubleshooting

### Agent Not Working As Expected?
1. Verify you copied the full "Custom Instructions" section
2. Check that Claude understood the role (ask "What is your role?")
3. Make sure you're working in the correct directory
4. Run the verification commands to check setup

### Need to Switch Agents?
1. Start a new Claude conversation
2. Copy instructions from the new agent file
3. Previous context won't carry over (this is intentional)

### Agent Collaboration?
- Each agent can reference other agent configurations
- Update shared documentation with discoveries
- Use consistent demo data across agents
- Coordinate through shared TODO files

## Success Tips

1. **Be Specific**: Tell the agent exactly what you want to accomplish
2. **Reference Files**: Mention specific files/functions when relevant
3. **Follow Patterns**: Ask the agent to follow existing patterns
4. **Test Incrementally**: Use diagnostic commands frequently
5. **Update Documentation**: Ask the agent to update reference docs with discoveries

Ready to start? Pick your agent and go! 🚀
# Claude AI Agent Instructions - SigmaSight Backend

**Purpose**: Instructions and preferences for Claude AI agents working on the SigmaSight backend codebase.

**Target**: Claude Code, Claude 3.5 Sonnet, and other AI coding agents

**Last Updated**: 2025-08-26

---

## 🎯 Primary References - READ FIRST

### **Essential Documentation**
1. **[AI_AGENT_REFERENCE.md](AI_AGENT_REFERENCE.md)** ⭐ **CRITICAL FIRST READ**
   - Complete codebase architecture and patterns
   - Import paths, database models, common errors
   - Eliminates 30-45 minutes of discovery time
   - **Always reference this before exploring the codebase**

2. **[TODO3.md](TODO3.md)** - Current Phase 3.0 API development (active)
3. **[TODO1.md](TODO1.md)** - Phase 1 implementation (complete)
4. **[TODO2.md](TODO2.md)** - Phase 2 implementation (complete)
5. **[README.md](README.md)** - Setup instructions and environment

### **Specialized References**
- **Batch Processing Issues**: See TODO1.md Section 1.6.14 for systematic issue resolution
- **Portfolio Reports**: See `_docs/requirements/PRD_PORTFOLIO_REPORT_SPEC.md` for specifications
- **Database Schema**: See AI_AGENT_REFERENCE.md for relationship maps and query patterns

---

## 🤖 Claude Agent Preferences & Instructions

### **1. Documentation Maintenance** 🔄 **IMPORTANT**
**Please update [AI_AGENT_REFERENCE.md](AI_AGENT_REFERENCE.md) whenever you discover:**
- New import patterns or module locations
- Changes to database schema or relationships  
- New batch processing issues or solutions
- Updated environment setup requirements
- New error patterns and their solutions

**Why**: This prevents future AI agents from re-discovering the same information and maintains institutional knowledge.

### **2. Working Style Preferences**

**✅ DO:**
- Read AI_AGENT_REFERENCE.md first to understand the codebase
- Check TODO3.md for current work, TODO1.md and TODO2.md for completed phases
- Use existing demo data (3 portfolios, 63 positions) for testing
- Implement graceful degradation for missing calculation data
- Follow async patterns consistently (avoid sync/async mixing)
- Use the diagnostic commands from AI_AGENT_REFERENCE.md
- Update completion status in TODO3.md as work progresses

**❌ DON'T:**
- Explore file structure without consulting the reference guide
- Create new test data when demo data exists
- Assume tables exist without checking (see stress_test_results issue)
- Mix async/sync database operations (causes greenlet errors)
- Ignore batch processing issues documented in TODO1.md 1.6.14
- **Add feature flags without explicit approval** - We prefer simple, correct implementations over complex toggles

### **3. Code Quality Standards**

**Database Operations:**
```python
# Always use async patterns
async with get_async_session() as db:
    result = await db.execute(select(Model).where(...))

# Handle UUID types properly  
if isinstance(id, str):
    uuid_obj = UUID(id)
else:
    uuid_obj = id
```

**Error Handling:**
```python
# Implement graceful degradation
try:
    calculation_data = await get_calculation_data()
except Exception as e:
    logger.warning(f"Calculation data unavailable: {e}")
    calculation_data = None  # Proceed with limited data
```

### **4. Task Management**
- Use TODO tools frequently for complex tasks (3+ steps)
- Mark TODO items complete immediately after finishing
- Document any new issues discovered in TODO1.md format
- Cross-reference related work in TODO files

---

## 🏗️ Current Codebase Status (Quick Reference)

### **✅ What's Working**
- Database models and relationships (except stress_test_results table)
- Demo data seeding (3 portfolios, 63 positions)
- 7/8 batch calculation engines (partial data available)
- Async database operations with proper patterns
- Greeks calculations (mibian library)
- Factor analysis and correlations

### **⚠️ Known Issues (see TODO1.md 1.6.14)**
- Batch processing has async/sync mixing issues
- Missing stress_test_results database table
- Market data gaps for certain symbols
- Treasury rate integration problems

### **🎯 Current Focus: Phase 2.0**
- Portfolio Report Generator implementation
- LLM-optimized output formats (MD, JSON, CSV)
- Using existing calculation data with graceful degradation
- Target: 3 demo portfolios

---

## 📋 Common Tasks & Patterns

### **Starting a New Feature**
1. Check AI_AGENT_REFERENCE.md for relevant patterns
2. Review TODO2.md for context and requirements  
3. Test imports with diagnostic commands
4. Implement with graceful degradation
5. Update TODO status and documentation

### **Debugging Issues**
1. Check TODO1.md 1.6.14 for known batch processing issues
2. Use diagnostic commands from AI_AGENT_REFERENCE.md
3. Verify database schema with `alembic upgrade head`
4. Test with demo data first
5. Document new patterns in AI_AGENT_REFERENCE.md

### **Database Operations**
1. Always use async patterns from AI_AGENT_REFERENCE.md
2. Handle UUID types properly (string vs UUID object)
3. Check table existence before querying critical tables
4. Implement graceful degradation for missing data

---

## 🔧 Environment Quick Start

```bash
# Essential verification commands (from AI_AGENT_REFERENCE.md)
uv run python -c "from app.models.users import Portfolio; print('✅ Models working')"
docker-compose ps  # Check PostgreSQL running
uv run alembic upgrade head  # Apply migrations
python scripts/reset_and_seed.py seed  # Seed demo data
```

---

## 💡 Efficiency Tips for Claude

1. **Read AI_AGENT_REFERENCE.md first** - saves 30-45 minutes of exploration
2. **Use completion notes** - update TODO2.md with detailed completion status
3. **Test incrementally** - use diagnostic commands frequently
4. **Document discoveries** - update AI_AGENT_REFERENCE.md for future agents
5. **Follow working patterns** - don't reinvent async database operations

---

## 📝 Communication Style

### **Progress Updates**
- Use clear completion markers: ✅ **COMPLETED**, ⚠️ **PARTIAL**, ❌ **FAILED**
- Include specific results: "Found 8 portfolios, 11 Greeks records"
- Document issues with references: "See TODO1.md 1.6.14 for resolution plan"

### **Problem Reporting**
- Be specific about error messages and context
- Reference existing documentation when applicable
- Suggest systematic solutions rather than quick fixes
- Update documentation with new patterns discovered

---

## 🎯 Success Metrics

**Good Claude Agent Session:**
- Minimal time spent on discovery (used AI_AGENT_REFERENCE.md)
- Clear progress tracking in TODO files
- Graceful handling of known issues
- Updated documentation for future agents
- Working code that follows established patterns

**Update This Document** when you discover:
- New codebase patterns or architectural insights
- Changes to database schema or model relationships
- New error patterns and their solutions
- Updated environment setup procedures
- New development workflow improvements

---

**Remember**: This codebase has substantial infrastructure already built. Your job is to build on the solid foundation, handle known issues gracefully, and document new patterns for future AI agents. The AI_AGENT_REFERENCE.md is your roadmap - use it!
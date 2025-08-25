# SigmaSight Custom GPT Kit (Backend-Aligned)
**Date:** 2025-08-24

This kit aligns GPT instructions with your **existing backend** so there are no conflicts.
- **Backend = Source of Truth for analytics (Greeks, VaR, stress tests, factors).**
- **GPT = Interpreter + Copilot: consumes backend JSON and explains it.**

## Key Adjustments
- Tools renamed to `get_*` to emphasize **retrieval** not recalculation.
- System Prompt updated: GPT **never recomputes core analytics**.
- Agent Tasks: focus on integration, schema validation, and explanation.
- Test plan & evals: check narrative correctness, schema compliance, gap detection.

## Contents
- SYSTEM_PROMPT.md
- TOOLS.md
- DATA_MAPPING.md
- AGENT_TASKS.md
- EVALS.md
- TESTPLAN.md
- SECURITY_PRIVACY.md
- DEPLOYMENT.md
- OBSERVABILITY.md

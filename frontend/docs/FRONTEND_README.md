# SigmaSight Frontend Build Pack (Agent-Led)
**Date:** 2025-08-24

This pack guides an AI coding agent (e.g., Windsurf) to implement a **backend‑aligned** frontend with:
1) **Chat + GPT Toolbar** (insight cards, tool triggers)
2) **Portfolio Page** (performance analytics; uses your provided component)
3) **Risk Page** (factor risks, exposures, scenario tiles)
4) **Targets & Tags Page** (position tagging, target prices, notes)

**Principle:** Backend is the *source of truth*. Frontend **never** recomputes risk; it **displays** backend JSON and asks GPT for interpretation.

Tech: **Next.js (App Router)**, **TypeScript**, **Tailwind + shadcn/ui**, **Recharts** for charts.

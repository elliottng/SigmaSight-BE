# SigmaSight GPT Skeleton
**Created:** 2025-08-24

This is a minimal code skeleton to run your **custom SigmaSight Analysis GPT** with a Fastify API,
tool endpoints, Zod schemas, a function-calling loop, and tests.

## What you get
- Fastify API with `/analyze` and `/tools/*` routes
- Zod schemas for inputs/outputs
- Deterministic math helpers (HHI, Effective N, weights normalization)
- Tool-calling loop (model can call your APIs)
- Example fixtures and Vitest unit tests

## Quick start
```bash
pnpm i
pnpm -w run build
pnpm -w run dev  # starts API on :8787
```
Environment variables go in `apps/api/.env` (see `.env.example`).

## Notes
- Model: `gpt-5-thinking`
- Temperature: 0
- The model returns both a readable summary and strict `machine_readable` JSON.

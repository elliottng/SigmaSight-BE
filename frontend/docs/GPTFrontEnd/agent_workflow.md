# Agent Workflow — Windsurf / AI Coding Agent

This document instructs an AI coding agent to implement the GPT-enabled frontend *without* conflicting with existing backend tools.

## North Star
- **Contract-first** workflow. Treat `api_contracts.md` as the source of truth.
- Do not rename or repurpose existing backend endpoints; add thin adapters if needed.
- Keep UI logic pure; no DB calls from the frontend.

## Steps
1. **Scaffold**
   - Next.js (app router), TypeScript, Tailwind, shadcn/ui.
   - Set up `env` handling for API base URL, auth token provider.

2. **Types & Clients**
   - Generate or handwrite TS types from `api_contracts.md`.
   - Create `/lib/api` with `fetchJson<T>()`, auth header injector, exponential backoff.

3. **Pages**
   - Implement: `/chat`, `/portfolio/[id]`, `/risk/[id]`, `/targets-tags/[id]`.
   - Each page fetches via server components for first paint, hydrates with SWR/React Query.

4. **GPT Toolbar**
   - A floating, collapsible toolbar with:
     - Prompt input
     - Context injectors (portfolioId, selected date range, selected positions)
     - Output renderer (cards + JSON inspector)
   - Calls `/v1/chat` (or your orchestrator) with `system_prompt.md` + user prompt + context.

5. **Components**
   - Build components listed in `components.md` with Tailwind + shadcn.
   - Keep props typed and serializable.

6. **Telemetry**
   - Emit events per `telemetry_analytics.md` to your analytics sink.

7. **Testing**
   - Contract tests against a mocked server (`msw`) using `api_contracts.md` fixtures.
   - Playwright for critical user flows.

8. **Performance**
   - Lazy-load heavy charts, memoize derived views, virtualize long lists.


# SigmaSight — GPT-Enabled Frontend Specs
Date: 2025-08-25

This package contains implementation-ready Markdown specs to build the SigmaSight frontend with a GPT toolbar and four core pages:

1. **Chat (GPT) Page** — with a GPT toolbar and analysis cards
2. **Portfolio Page** — summary & attribution (wired to your DB)
3. **Risk Page** — factor exposures, VaR/ES hooks, stress tests
4. **Targets & Tags Page** — tagging taxonomy + target prices

The specs assume:
- Next.js / React + Tailwind + shadcn/ui
- TypeScript on the frontend
- A thin API layer (FastAPI or Node/Express) that wraps your existing backend tools
- Authentication handled via your existing session (e.g., JWT / NextAuth)
- Database per `DATABASE_DESIGN_V1.4.md` (see `db_mapping.md` to align field names)

> **Contract-first**: The `api_contracts.md` defines typed responses your frontend will consume. If your backend differs, update the contracts and regenerate TS types with `openapi-typescript` or by hand.

**Folders in this zip**
- `system_prompt.md` – production system prompt for the GPT agent
- `agent_workflow.md` – how your AI coding agent should build & ship
- `api_contracts.md` – REST/HTTP contracts (stable, versioned)
- `db_mapping.md` – mapping to your DB schema (adjust per actual names)
- `chat_page.md` – UX + component tree + data flows
- `portfolio_page.md` – wiring for your provided dashboard code
- `risk_page.md` – factor & forward-looking risk UI + calc adapters
- `targets_tags_page.md` – tagging & target price UX + rules
- `components.md` – shared UI primitives & composition
- `telemetry_analytics.md` – event schema for product analytics
- `security_compliance.md` – authz, PII, rate limits & logging
- `testing_plan.md` – unit/integration/contract tests, fixtures


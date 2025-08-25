# SigmaSight Frontend API Proxies & Hooks
**Date:** 2025-08-25

This bundle gives you **Next.js App Router API proxies** and **React Query hooks** that call your backend `get_*` tools without duplicating analytics.

- Proxies live under `/app/api/portfolio/[id]/*` and forward to `BACKEND_BASE`.
- Hooks live under `/lib/hooks/*` and power the 4 pages: Chat, Portfolio, Risk, Targets.
- Types in `/lib/types.ts` mirror tool responses; adjust fields to match your DB design (DATABASE_DESIGN_V1.4.md).
- A mapping guide (`FIELD_MAPPING.md`) shows where each UI field comes from.

Set env:
```
NEXT_PUBLIC_BACKEND_BASE=https://api.your-backend.com
SIGMASIGHT_API_TOKEN=dev-token
```

Drop these into your Next.js repo root.

# Unresolved Questions & Inconsistencies (2025-07-15)

> The following items were flagged by the coding agent after a full review of the current SigmaSight documentation and legacy notes.  Clarifying these early will prevent re-work and ensure that all contributors share the same mental model.

## 1. Folder / Path Conventions
- Requirements live under `sigmasight-BE/docs/requirements`, but new project files (e.g., `TODO.md`, future `README.md`) sit one level higher.
- Relative links in `TODO.md` that start with `./sigmasight-BE/docs/...` will break when viewed from the repo root.
- `legacy_scripts_for_reference_only` contains Python code yet is nested inside the *docs* tree—unexpected for contributors.

## 2. Version Labels
- PRD / API / DB specs are tagged **v1.4** while the prototype doc is **V5**.
- Readers may assume these are different product generations. A short note that *v1.4 = documentation revision* and *V5 = frontend prototype version* would help.

## 3. Market-Data Requirements
- PRD emphasises *pre-calculated* analytics, but API spec exposes endpoints that imply on-demand calculation.
- CSV spec & DB design store tickers, but only legacy scripts describe where GICS sector data lands in the schema.

## 4. Authentication Scope
- PRD calls for multiple demo accounts, yet DB design shows no `users` table excerpt—only foreign-key references.
- API spec omits `/auth/login` and `/auth/register` endpoints required for testers.

## 5. Options / Greeks Handling
- API endpoints return detailed Greeks, but PRD (Phase 1) says "mock options Greeks display".
- Decision needed: store dummy values vs. calculate with simplified Black-Scholes on every request.

## 6. Tag & Strategy Tag Storage
- CSV spec, Positions endpoints and prototype reference tags, but DB design lacks tables or JSON fields for them.
- Need either a `tags` lookup + many-to-many join or a JSONB array with indexing guidance.

## 7. Async vs. Sync API Modes
- API spec mentions both modes but doesn’t mark which endpoints are async-only (polling) versus synchronous.
- A simple column in the endpoint table would clarify.

## 8. Naming & Capitalisation
- Endpoint nouns mix singular and plural (`/portfolio`, `/positions`, `/strategies`).
- File names vary in style (`V0_V5_FRONT_END_PROTOTYPE_FEATURES.md`, `API_SPECIFICATIONS_V1.4.md`). Consistent snake-case or kebab-case is easier to reference.

## 9. Deployment Details
- PRD references Railway + **UV** package manager; TODO lists `uv` but doesn’t explain integration into FastAPI start-up.
- A short deployment note in the main README would help.

## 10. Legacy Script Guidance
- Legacy README says *“DO NOT copy infrastructure code (S3, Parquet)”* yet scripts largely demonstrate Parquet ingestion.
- Clarify which parts are for reference (API usage, data shapes) and which to ignore.

---

**Next Step:** Confirm or refine these points, then update the relevant docs (PRD, API spec, DB design, TODO.md) so future contributors—and automated agents—have a single, consistent source of truth.

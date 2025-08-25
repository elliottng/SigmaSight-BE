# Targets & Tags Page — Tagging & Target Prices

Route: `/targets-tags/[id]`

## Goals
- Allow users to organize positions via tags (strategy, theme, basket).
- Capture **target price** and **stop** per position with validation.

## Layout
- Left: **Tag Manager**
  - List of tags with color + description
  - Create/edit/delete
  - Bulk assign via multi-select table
- Right: **Targets Table**
  - Columns: Ticker, Qty, Avg Cost, Price, Target, Stop, Distance to Target, Notes
  - Inline edit with optimistic updates

## API
- Tags:
  - `GET /v1/tags?portfolioId=...`
  - `POST /v1/tags` (create/update)
  - `POST /v1/tags/assign` (bulk)
- Targets:
  - `GET /v1/targets?portfolioId=...`
  - `POST /v1/targets` (upsert array)

## Validation
- Target and stop must be positive numbers; stop < price < target (optional rule toggle).
- Persist editor state; warn on unsaved changes.


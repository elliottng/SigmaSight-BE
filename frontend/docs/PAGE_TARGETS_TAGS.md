# /targets — Targets & Tags

## UI
- Table: position (symbol, name), current price, target price (editable), tags (multi-select), notes
- Bulk actions: add tag to selection, clear tags, set % move target
- Side panel: position details and history (last tags, prior targets)

## API
- `GET /api/portfolio/:id/targets`
- `POST /api/portfolio/:id/targets` (batch upsert)
- `GET /api/portfolio/:id/positions` (for symbols, names)

## Data Contract
- Target: { position_id, target_price, target_date?, rationale? }
- Tags: { position_id, tags: string[] }

## Acceptance
- Edits are optimistic with rollback on error
- Unsaved changes guard on navigation
- Keyboard-friendly tag editing

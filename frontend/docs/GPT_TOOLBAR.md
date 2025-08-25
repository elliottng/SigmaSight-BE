# GPT Toolbar (Top Bar + Side Panel)

## Purpose
Let users ask questions, run one-click tool prompts, and pin AI summaries.

## UI
- Search-like input with "Ask SigmaSight…"
- Quick actions: "Explain exposures", "Top 3 risks", "Hedge ideas", "Explain factor move"
- Results drawer with markdown + small cards (beta, top factor, best/worst scenario)

## Data Flow
- On submit: POST to `/api/gpt/analyze` with current portfolio_id and user prompt
- Backend calls GPT (which calls **get_*** endpoints) and returns
- Render `summary_markdown` and `machine_readable` cards

## Acceptance
- Input debounced
- Handles tool progress states (idle/loading/error)
- Renders markdown safely (rehype-sanitize)

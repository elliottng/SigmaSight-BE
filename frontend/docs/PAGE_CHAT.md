# /chat — Chat + GPT Toolbar

## Layout
- Left: chat stream (bubbles)
- Right: insight cards (sticky on desktop; collapsible on mobile)
- Top: GPT Toolbar

## Interactions
- User prompt → `/api/gpt/analyze` (payload: { portfolio_id, question, contextFlags })
- Response:
  - Render `summary_markdown` in chat
  - Populate cards from `machine_readable`: snapshot, concentration, top factors, best/worst scenarios

## Cards (examples)
- Snapshot: invested %, net, gross
- Concentration: Top1/3/5, effective N
- Factors: top 3 by exposure
- Scenarios: best/worst by pnl_pct

## Acceptance
- Chat persists per portfolio session
- Cards update when new responses arrive

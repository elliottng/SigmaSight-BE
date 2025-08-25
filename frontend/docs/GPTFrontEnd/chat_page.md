# Chat (GPT) Page — UX & Data Flow

Route: `/chat`

## Layout
- Left: Conversation pane with a **GPT Toolbar** docked at the top.
- Right: **Insight Cards** panel (sticky) rendering structured outputs (JSON -> cards).

## GPT Toolbar
- Prompt input
- Context chips:
  - Portfolio selector
  - Date range (asOf/window)
  - View: portfolio | longs | shorts
  - GroupBy: security | sector | factor
- Submit -> calls your orchestrator which invokes the model with `system_prompt.md` + user prompt + context.
- Responses may include a `cards[]` array (JSON) to render common widgets (exposure bars, top N lists).

## Insight Cards (examples)
- **Exposure Snapshot** (net/gross/long/short)
- **Top Contributors/Detractors**
- **Factor Tilt** (bar list)
- **Risk Summary** (VaR/ES with notes)
- **What-If Result** (before/after/deltas)

## Empty State Prompts
- “Show my top 5 contributors over the last month and any concentration risks.”
- “Model selling half of my top 3 growth longs; what happens to Growth beta?”


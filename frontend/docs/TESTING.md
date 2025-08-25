# Frontend Testing Plan

## Unit
- Component prop rendering (MetricCard, ContributionCard)
- Store reducers (edits, filters)

## Integration
- Pages render with mocked API clients
- /chat posts prompt and renders summary + cards

## E2E (Playwright)
- Navigation across 4 pages
- Edit targets and persist
- Changing period/view triggers refetch

# Testing Plan

## Unit
- Components: render + props contracts
- Hooks: data fetching, error paths

## Integration
- `msw` to stub API per `api_contracts.md` fixtures
- Flows:
  - Load portfolio page, see metrics & attribution
  - Change period/view and re-fetch
  - Risk page: change VaR method & horizon
  - Targets & Tags: create tag, assign to 3 positions, set targets

## Contract
- Validate backend responses against schemas (zod) before render
- Report schema drift with actionable error messages

## E2E
- Playwright: smoke paths for the 4 pages + GPT prompt round-trip

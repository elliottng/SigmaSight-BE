# Agent Tasks (Backend-Aligned)

## Mission
Connect GPT to backend APIs; avoid duplicating analytics logic.

## Tasks
1. Scaffold connectors for all `get_*` tools.
2. Validate responses against schema.
3. Pass data into GPT; collect summary + machine_readable output.
4. Ensure missing inputs → listed under `gaps`.
5. Write integration tests (fixtures → GPT outputs).

## Acceptance Criteria
- GPT never attempts to compute VaR, Greeks, factors, stress tests.
- All outputs conform to schema.
- Missing data → clear gap messages.

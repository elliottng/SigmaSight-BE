# Test Plan (Backend-Aligned)

## Unit
- Schema validation of backend responses
- Gaps detection

## Integration
- Feed full payload (exposures, factors, stress) → GPT outputs correct summary

## Regression
- Golden tests with fixtures (expected narrative + machine_readable)

## Performance
- Responses under 3s for portfolios ≤ 200 positions (since backend precomputes)

# Engineering Rules

- No feature flags at this stage. We are in a functional prototype phase with no customers; implement changes directly without flags or staged rollouts.
- Prefer clarity over premature abstraction. Keep implementations simple and explicit.
- Document material behavior changes in `_docs/requirements/` and reference affected modules (e.g., `app/calculations/factors.py`).
- When redesigning analytics, preserve storage interfaces (e.g., `FactorExposure.exposure_value` for betas; `exposure_dollar` for reporting) to avoid breaking downstream stress testing.
- Avoid zero-filling analytical return series; preserve NaNs and handle alignment explicitly at regression/aggregation steps.

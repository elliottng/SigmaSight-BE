# Telemetry & Analytics

Emit events to your analytics sink (Segment/Snowplow/etc.).

## Event Schema
- `view_exposure_dashboard` { portfolioId, window }
- `run_var` { portfolioId, method, conf, horizon, durationMs, success }
- `whatif_model_run` { portfolioId, nTrades, durationMs, success }
- `gpt_prompt` { tokensIn, tokensOut, durationMs, success, errorType? }
- `tool_error` { toolName, endpoint, status, message }

## PII
- Never include account numbers or personal identifiers.
- Hash portfolioId if required by policy.

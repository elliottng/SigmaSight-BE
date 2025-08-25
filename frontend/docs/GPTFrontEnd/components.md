# Shared Components

- **GPTToolbar**: prompt input, context chips, submit, streaming response
- **MetricCard**: label/value; skeleton support
- **AttributionTickerCard**: ticker + contribution pct; color by sign
- **ContributionCard**: label + value; +/- colored
- **ExposureBars**: net/gross/long/short stacked
- **FactorBarList**: factors with betas or % variance
- **RiskCards**: VaR/ES + notes
- **TargetsTable**: virtualized table with inline editors
- **TagPills**: colored labels with add/remove
- **JsonInspector**: collapsible pretty-print for GPT JSON payloads

Props must be serializable and typed. Avoid passing functions through boundaries that block React server rendering.

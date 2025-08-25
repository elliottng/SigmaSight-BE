# Shared UI Components

- `<MetricCard label value />` — small stat
- `<Sparkline data />` — tiny trend
- `<Pill value intent />` — colored pill (+/-)
- `<DataTable columns data />` — shadcn/ui table wrapper
- `<KPIGroup items />` — grid of MetricCard
- `<Section title actions?>` — consistent sections

## Acceptance
- Components are **presentational**; data arrives via props
- All cards aria-labelled; keyboard accessible; tab order logical

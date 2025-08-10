# Factor Beta Redesign (Phase 2.6.8)

Status: Proposed — Awaiting Review
Last Updated: 2025-08-09 (local time)
Owners: Risk/Analytics

---

## 1. Summary

Observed unrealistic portfolio factor betas (e.g., Market betas near ±3 and frequent capping). Root cause is upstream beta estimation rather than the position-level attribution (Option B), which is correct. This document proposes a redesign of the beta estimation to produce stable, realistic, and institutionally-aligned factor betas that integrate cleanly with existing storage, factor dollar exposures, and stress testing.

Key points:
- Position-level attribution for factor dollar exposures in `aggregate_portfolio_factor_exposures()` is correct and should remain as-is.
- Stress testing P&L uses `FactorExposure.exposure_value` (portfolio-level beta), not `exposure_dollar`.
- Notional and delta-adjusted exposures are independent of factor betas and remain unaffected.

Plain-English quick primer (what the terms mean):
- Beta: how sensitive a position/portfolio is to a risk factor. Beta = 1 to “Market” means if the market moves +1%, we expect about +1% move in the position (on average).
- Returns used in regressions: percentage daily changes (e.g., 0.01 = 1%), not dollars.
- OLS regression: a statistical fit that finds the line best explaining position returns from factor returns. “Univariate” = one factor at a time; “multivariate” = all factors together.
- Delta (for options): how much an option price changes when the underlying moves. Using delta-adjusted returns can make option-vs-factor relationships less noisy.
- NaN vs zero: missing data (NaN) should usually be dropped/aligned, not turned into zeros, which can bias results.

Do not implement until this plan is reviewed and approved.

---

## 2. Current Implementation (Relevant Code)

- `app/calculations/factors.py::calculate_factor_betas_hybrid()`
  - Per-position, per-factor univariate OLS regressions with intercept.
  - Capping betas at ±`BETA_CAP_LIMIT` (currently 3).
  - Uses position return series derived from exposure %. For options, delta adjustment is optional (default False).
  - Plain-English: “Univariate” means we fit one factor at a time. This is simple but can over-attribute risk to whichever factor looks strongest if factors move together. The cap is a safety net to prevent extreme numbers when data is noisy.
- `app/calculations/factors.py::calculate_position_returns()`
  - Builds a time series of exposure per position using price × quantity × multiplier; for options, optionally multiplies by delta.
  - Computes returns via `.pct_change()`; currently fills missing values with zeros.
- `app/calculations/factors.py::aggregate_portfolio_factor_exposures()` and `_aggregate_portfolio_betas()`
  - Correct position-level attribution for factor dollar exposures and exposure-weighted portfolio betas.
- `app/calculations/market_data.py::fetch_historical_prices()`
  - Provides close price histories; factor returns computed as decimal daily returns via `.pct_change()`.

---

## 3. Legacy Reference: Methods and Differences vs Current

This section summarizes the legacy reference scripts in
`sigmasight-backend/_docs/requirements/legacy_scripts_for_reference_only/legacy_analytics_for_reference/`
and contrasts them with the current SigmaSight implementation.

3.1) Legacy data and returns
- __Function__: `get_data.py::calculate_daily_returns()`
- __Method__: Uses NYSE trading calendar to step to the previous valid trading day; computes price-based daily returns per ticker as `close / prev_close - 1`.
- __Handling__: If no previous close, sets `NaN` (no zero-fill). Output columns are per-ticker return series (e.g., `SPY_ret`).

3.2) Legacy beta estimation
  - __Portfolio-level style betas__: `get_data.py::calculate_betas()` runs multivariate OLS via `statsmodels` with an intercept: predictors = factor return columns, dependent = portfolio return (last column). Betas taken from `model.params[1:]`.
  - __Position-level betas__: `factors_utils.py::calculate_position_betas()` merges long-form factor and position returns; sets
   `factor_rf = factor_return - mean(factor_return by factor)` and
   `position_rf = position_return - mean(factor_return by position)` (as coded), then computes
   `beta = cov(position_rf, factor_rf) / var(factor_rf)` via grouped covariance and variance.
   Note: The `position_rf` construction appears inconsistent (uses factor returns’ mean rather than position returns’ mean); and the covariance-ratio is per-factor (univariate), susceptible to omitted-variable bias.

3.3) Legacy factor covariance/correlation and VaR
- __Covariance__: `var_utils.py::covariance_matrix()` uses `factor_returns.cov()`.
- __Exponential-decay covariance__: `var_utils.py::decay_covariance_matrix()` applies a 0.94 decay schedule before `cov()`.
- __Correlation__: `var_utils.py::correlation_matrix()` computes `factor_returns.corr()` and maps to factor names.
 - __VaR (matrix form)__: `var_utils.py::multiply_matrices()` computes
  `sqrt( exposure^T · betas · covariance · betas^T )`, i.e., a classic factor-model VaR.
  - Why this matters: this formula says total portfolio risk comes from how big your exposures are, how sensitive they are to factors (betas), and how those factors co-move (covariance).
 
  Plain-English: what these tools mean
  - Covariance vs correlation: covariance measures co-movement in units of returns; correlation is the unitless, scaled version of covariance in [-1, 1].
  - Exponentially decayed covariance: puts more weight on recent data to reflect current market regimes while still using history.
  - Matrix VaR: uses betas and the factor covariance matrix to turn exposures into a single probabilistic risk number (e.g., 95%/99% VaR). Diversification is naturally captured via off-diagonal covariances.
 
  Current system vs proposed redesign
  - We keep the existing correlation-based stress testing (exponentially weighted correlation with caps) and do not enable matrix VaR in this redesign.
  - The redesign focuses on improving betas (section 7), which will feed cleaner inputs into the same stress engine.
 
  Impact of not using matrix VaR now
  - Pros: simpler stakeholder communication; less sensitivity to noisy covariance estimation while we stabilize betas.
  - Cons: no single-number probabilistic risk metric or marginal risk contributions until matrix VaR is (re)introduced.
 
  Future addition (out of scope here)
  - After betas stabilize, we can add matrix VaR by reusing the legacy simple/decayed covariance patterns and matrix multiplication path alongside stress testing.

3.4) Legacy conventions and libraries
- __Missing data__: Preserves `NaN` rather than imputing zeros prior to regression.
- __Regression library__: `statsmodels` OLS.
- __Computation__: Primarily on-demand; no explicit caching visible.
  - Why this matters: treating missing data as “0% return” falsely implies no movement occurred; keeping `NaN` and aligning/dropping missing rows avoids systematic bias.

3.5) Comparison vs Current State (today)
- 3.5.1 __Returns__
  - Legacy: price-based returns per ticker; preserves `NaN`.
  - Current: exposure-based position returns via `calculate_position_returns()` using `.pct_change()` on exposure time series; currently zero-fills missing values.
  - Redesign: remove zero-fill; inner-join with factor returns and drop `NaN`; default delta-adjusted path for options.
  - Plain-English: zero-filling is like pretending we had a flat return on missing days, which can artificially shrink or distort relationships. Dropping missing rows keeps analysis to days when both series exist.
- 3.5.2 __Betas__
  - Legacy: portfolio-level multivariate OLS; position-level per-factor covariance ratio (univariate with respect to each factor).
  - Current: univariate OLS per factor per position with hard cap ±`BETA_CAP_LIMIT`.
  - Redesign: multivariate OLS per position across all factors simultaneously, with quality gates and winsorization; remove hard emergency caps.
- 3.5.3 __Missing data & quality__
  - Legacy: no zero-fill; fewer implicit biases from imputation.
  - Current: zero-fill introduces bias; warnings observed; many betas hit caps.
  - Redesign: enforce `MIN_REGRESSION_DAYS`, preserve `NaN` by inner-join and drop, store diagnostics (R², p-values, std err).
- 3.5.4 __Covariance/Correlation & VaR/Stress__
  - Legacy: provides simple and decayed covariance matrices and a VaR matrix multiplication routine.
  - Current: stress testing uses an exponentially weighted correlation matrix and scenario impacts; factor betas (`FactorExposure.exposure_value`) drive P&L, dollar exposures are reporting-only.
  - Redesign: no change to stress testing mechanics; improved betas should yield more realistic scenario P&L.
- 3.5.5 __Aggregation & usage__
  - Legacy: matrix-based VaR uses exposures × betas × covariances.
 - Current: Option B position-level attribution for factor dollar exposures is in place and correct; stress uses portfolio betas.
 - Redesign: preserve existing storage and attribution paths; only change beta estimation pipeline.

3.6) Legacy Implementation Insight
 - Discovery: The legacy system used a mixed approach - multivariate for portfolio-level betas but univariate (covariance method) for position-level betas.
 - Interpretation: The legacy developers likely recognized the importance of multivariate regression but made computational trade-offs at the position level.
 - Our proposal: Moving to multivariate at both levels is computationally feasible with modern hardware and will eliminate the omitted variable bias.


## 4. (unused)
---

## 5. Problems Observed

- Omitted variable bias from univariate regressions inflates coefficients and double-counts exposure across factors.
- Options using option-price returns (high variance) vs factor ETF returns (lower variance) tend to yield oversized slopes if not delta adjusted.
- Zero-filling returns distorts variance/covariance and biases regressions.
- Insufficient or irregular data can lead to unstable fits and runtime warnings.

### 5.1 Critical Discovery: Severe Multicollinearity (2025-01-10)

Investigation of the factor ETFs revealed extreme multicollinearity:
- **Factor correlations**: Up to 0.96 (Size vs Value), with 17 pairs having |r| > 0.7
- **VIF values**: Quality (52.5), Growth (41.8), Value (23.9), Size (22.0) - all indicating severe multicollinearity
- **Condition number**: 640+ indicating numerical instability
- **Impact**: Standard multivariate OLS produces MORE extreme betas than univariate due to this multicollinearity

This explains why the simple univariate approach has been relatively stable - it avoids the multicollinearity problem entirely.
 
 Plain-English: why these problems happen
 - Univariate fits look at one factor at a time, so if factors move together, each one can get “too much credit,” inflating betas.
 - Options can swing more than ETFs; without delta adjustment, regressions can latch onto noise instead of signal.
 - Replacing missing values with 0% return is like pretending nothing happened on that day; this skews averages and correlations.
 - If we don’t have enough overlapping days between a position and factors, the fit is shaky and statistical warnings pop up.

---

## 6. Design Goals

- Produce realistic, stable factor betas at the position and portfolio levels.
- Use appropriately scaled, comparable daily return series for regressions.
- Be robust to missing data without biasing estimates.
- Preserve existing interfaces: continue storing position-level and portfolio-level betas, with factor dollar exposures computed from position-level attribution.
- Ensure downstream stress testing remains correct (P&L uses betas, not dollar exposures).

Plain-English: what “stable and realistic” looks like
- Fewer extreme betas pinned at the cap; most equity betas near sensible ranges (e.g., around 1 vs “Market”, unless hedged or special cases).
- Better model fit diagnostics (higher R² where appropriate, reasonable p-values), indicating factors explain position moves without overfitting.
- Consistent results across adjacent days; small changes in inputs don’t swing betas wildly.

---

## 7. Proposed Redesign

7.1 Return computation clarification
    - Compute position returns on prices directly: `prices.pct_change()`.
    - Under constant quantity/multiplier, `pct_change(price × constant) == pct_change(price)`; computing on prices is equivalent and clearer.
    - Remove zero-filling from return series; NaN handling occurs via inner-join with factor returns and dropping rows before regression.

7.2 Multivariate regression per position (Original Proposal)
    - Replace per-factor univariate OLS with a single multivariate OLS per position using all factor return columns simultaneously (plus intercept) over aligned dates.
    - Use `statsmodels.api.OLS(y, sm.add_constant(X_multi)).fit()`; extract betas from `params[1:]` mapped to factor names.
    - Rationale: removes omitted variable bias and reduces inflated betas.
    - Plain-English: fit "all factors together" so we don't double-count shared movements. This typically yields more balanced, realistic betas.
    - **WARNING**: Testing revealed severe multicollinearity (see Section 5.1), making this approach numerically unstable without regularization.

7.2.1 Alternative Approaches (Based on Multicollinearity Discovery)
    
    **Option A: Ridge Regression (L2 Regularization)**
    - Use Ridge regression instead of OLS to handle multicollinearity
    - Penalizes large coefficients, producing more stable betas
    - Requires choosing regularization parameter (alpha)
    - Implementation: `sklearn.linear_model.Ridge` or equivalent
    
    **Option B: Principal Component Regression (PCR)**
    - Transform correlated factors into orthogonal principal components
    - Run regression on components, then transform back to factor space
    - Reduces dimensionality while preserving most variance
    - More complex interpretation but handles multicollinearity well
    
    **Option C: Elastic Net**
    - Combines L1 and L2 regularization
    - Can perform feature selection (zeroing out less important factors)
    - Good middle ground between Ridge and LASSO
    
    **Option D: Improved Univariate with Better Data Handling**
    - Keep univariate regression (one factor at a time) to avoid multicollinearity entirely
    - Focus on data quality improvements:
        - Remove zero-filling of returns ✓
        - Better alignment and NaN handling ✓
        - Apply winsorization instead of hard caps ✓
        - Mandatory delta adjustment for options ✓
    - Simpler, more stable, already working reasonably well
    - Accept some omitted variable bias as trade-off for stability
    
    **Recommendation**: Given the severity of multicollinearity (VIF > 50, correlations > 0.95), Option D (improved univariate) is the most pragmatic choice for immediate implementation, with Option A (Ridge) as a future enhancement.

7.3 Make delta-adjusted returns mandatory for options
    - In `calculate_factor_betas_hybrid()`, enforce `use_delta_adjusted=True` when calling `calculate_position_returns()` (no per-portfolio override in this phase).
    - Keep fallback to dollar exposure when delta is unavailable, but log quality degradation.
    - Optional future improvement: for options, consider constructing the exposure series off the underlying price series × delta × multiplier × quantity to further reduce noise.
    - Plain-English: treat options as a scaled version of the underlying’s move (via delta) so their link to factors is less noisy.

7.4 Missing data handling and alignment
    - Remove zero-filling of returns. For each position, inner-join `y` (position returns) with `X_multi` (factor returns) and drop rows with NaNs prior to regression.
    - Enforce per-position minimum sample requirement (e.g., `MIN_REGRESSION_DAYS`). If not met, skip regression for that position, set betas to 0, log, and set low-quality flag.
    - Plain-English: only compare days where both series exist; require “enough days” to trust the fit, otherwise mark as low-quality.

7.5 Quality controls and outlier handling
    - Prefer quality gating to hard caps: check R², standard errors, and p-values per beta.
    - Apply winsorization on the final beta distribution at the 1st/99th percentile; do not use a hard ±3 cap.
    - Do not use a hard emergency cap; rely on winsorization and quality gating. Log and alert on any extreme values that remain post-winsorization.
    - Plain-English: look at model “health checks” (fit quality and error bars) and tame only the far-out tail via winsorization; there is no last-resort cap.

7.6 Diagnostics, logging, and observability
    - Persist `regression_stats` per position: R², p-values, std errors, residual diagnostics (for audit and debugging).
    - Add a one-off analyzer script to generate beta histograms, R² distributions, and outlier counts (beyond winsorization thresholds) before/after this redesign.
    - Plain-English: keep simple dashboards/stats so we can see distributions, spot issues early, and prove improvements.

7.7 Storage and downstream usage
    - Continue storing position-level betas and portfolio-level betas as currently done.
    - Factor dollar exposures remain position-level contributions: sum(position signed dollar exposure × position beta) — unchanged.
    - Stress testing continues to use `FactorExposure.exposure_value` (beta) for P&L; `exposure_dollar` remains reporting-only.

---

## 8. Implementation Plan

The detailed implementation plan, including the task list and progress, is tracked in the main project `TODO2.md` file under **Phase 2.7: Factor Beta Redesign**.

This document will remain the source of truth for the *design*, while `TODO2.md` is the source of truth for the *execution*.

---

## 9. Acceptance Criteria

- No betas truncated by a hard cap; outliers beyond winsorization thresholds are near-zero (target: ~0%).
- Market betas for equities mostly within [-1.5, 1.5]; options may extend but with significantly fewer extreme values.
- Improved R² distribution; reduction in regression warnings.
- Factor dollar exposures no longer each claim ~90% of gross exposure; more reasonable splits by factor.
- Stress test scenario impacts become more realistic without code changes in stress testing modules.

---

## 10. Non-Goals / Out of Scope

- Redesign of factor dollar exposure attribution (already corrected by Option B).
- Changes to notional or delta-adjusted exposure calculations (remain independent and correct).
- Database schema changes; continue using existing `PositionFactorExposure` and `FactorExposure` records.

---

## 11. Risks and Mitigations

- Data sparsity for some symbols or factors → enforce per-position minimum days; mark low-quality; consider robust regression later.
- Options still noisy even with delta adjustment → consider underlying-price-based exposure series in a future enhancement.
- Performance considerations with multivariate fits → acceptable for current scale; monitor and optimize if needed.

---

## 12. Decisions

- **Regression approach**: Option D (Improved Univariate) due to severe multicollinearity in factor ETFs
  - Keep univariate regression to avoid numerical instability
  - Apply data quality improvements (no zero-fill, winsorization, better alignment)
  - Consider Ridge regression (Option A) as future enhancement
- **Delta-adjustment**: Mandatory for options; no per-portfolio override in this phase. If delta is unavailable, fall back to dollar exposure and mark low-quality.
- **Emergency cap**: None after winsorization and quality gating; remove the hard cap.
- **Diagnostics**: Yes — persist detailed regression diagnostics (R², p-values, std err, residual checks) for audit/debugging and monitoring.

---

## 13. References

- `app/calculations/factors.py`
- `app/calculations/market_data.py`
- `sigmasight-backend/_docs/requirements/FACTOR_EXPOSURE_REDESIGN.md`

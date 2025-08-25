# Evaluation Plan (Backend-Aligned)

## Eval A: Exposures Only
Input: snapshot JSON only
Expect: GPT reports exposures + "gaps" for missing factors, stress tests

## Eval B: Full Factors
Input: snapshot + factor exposures
Expect: GPT narrates factor tilts; no recomputation

## Eval C: Stress Scenarios
Input: stress test results
Expect: GPT lists best/worst scenarios with % PnL (from backend)

## Eval D: Missing Var
Input: snapshot with no VaR
Expect: GPT adds "gap: missing VaR"

Pass = GPT respects backend outputs, does not hallucinate metrics

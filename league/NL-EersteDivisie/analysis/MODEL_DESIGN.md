# Phase 4 — model design sketch (not fitted)

This is a design document only. No model fitting, preregistration, engine, or virgin read has been performed.

## Shared validation frame

**dev = 2021/2022 warm-up, scored dev 2022/2023-2024/2025 (n=1140); virgin = 2025/2026 (complete, n=380) read ONCE dev-passers only; 2026/2027 partial reserved confirmatory, never touched.**

Primary lines come from the DEV distribution (2021/2022–2024/2025): choose the line nearest the dev median for SOT, corners, cards, and total shots, and report mean plus over-rate for each candidate line. Goals primary line is OU2.5. EDA levels of 2025/2026 are design aggregates only and do not set a line, gate, or arm.

The frozen descriptive DEV line table is: SOT line 9.5 (mean 9.644, over-rate 48.75%); corners line 9.5 (mean 10.071, over-rate 55.00% at 9.5 vs 41.97% at 10.5 — 9.5 is closest to 0.5; coordinator correction of the first-pass table, which did not apply its own nearest-median rule); cards line 3.5 (event-unified mean 3.163, over-rate 41.25% at 3.5 vs 61.91% at 2.5 — 3.5 closest to 0.5); total-shots line 25.5 (mean 26.019, median 26, over-rate 50.79% at 25.5 vs 43.68% at 26.5 — 25.5 closest to 0.5).

## Candidates and feasibility

| candidate | Gate Zero | permitted variant arms | feasibility |
|---|---|---|---|
| G goals | goals-only Dixon-Coles | SHRINK; X2 mover prior | feasible; no xG blend |
| S SOT | v5 pattern, no xG inputs | RS ridge/ratio shrink, BB prior 200 -> 20,000 | feasible; SOT is complete |
| C corners | X9 possession/big-chance Gate Zero | X7 touches_opp_box only | feasible but X7 is coverage-gated |
| K cards | team card Gate Zero | X8 referee arm (adopted: coverage 95.8-100% in scored dev, strictness r=0.420) | feasible with event-unified yellows |
| T total shots | arm A v1 | arm B v2 level; arm C E9 trailing-r | feasible; descriptive target levels exist |

Goals arms are exactly Gate Zero (DC goals-only), SHRINK (frozen <6 prior-match rating shrink, as the DE-3Liga G prereg), and X2 mover arm only because FEATURES adopts X2. SOT arms are exactly Gate Zero (v5 pattern, no xG inputs) and RS ridge/ratio shrink with BB prior 200 -> 20,000, as S-NL RS. Corners are Gate Zero (X9) plus X7 only if adopted. Cards are Gate Zero plus X8 (adopted in FEATURES, coordinator correction). X2's magnitudes are the coordinator-verified relegated-club pooled gaps: attack +0.419, GA -0.199. Total shots are A (v1), B (v2 level), and C (E9 trailing-r), with no additional arms.

## Gates

Dev goals beats climatology on 1X2 LL AND RPS AND base rate on OU2.5 LL else FAIL variants moot; counts beat base rate AND naive trailing-10 on primary LL else FAIL. Virgin: PASS if LL <= best baseline AND |calibration| <= 1pp; PROVISIONAL if breach <= 1 SE; else FAIL. Calibration = actual - predicted. No dev pass => virgin NOT read.

The half-share constants in FEATURES are reporting constants only; no candidate may fit a team-specific halves model. X2 remains subject to the same gates because the mover labels are proxy labels, not cross-tier truth.

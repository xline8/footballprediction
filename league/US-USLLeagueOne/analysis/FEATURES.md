# Phase 3.5 — Feature Engineering: USA USL League One

Trailing or expanding-with-decay windows are strictly pre-match; ratios are
ratios of sums; missing values deactivate an arm and are never filled.

## §1 Template features — verdicts

### X1 — Goals observation pair — **ADOPTED, goals-only**
No xG exists and shotmap coverage is 0%. The DC goals-only pattern is the
complete G-USLL1 fit.

### X2 — Mover tier offset — **DROPPED**
There is no pro/rel mover population. Churn is expansion, voluntary division
moves, and departures/folding as documented in DATA_UNDERSTANDING.md. Thin-
team risk goes to the SHR arm; imported offsets are rejected.

### X3 — Set-play xG — **DROPPED**
No xG or set-play source exists.

### X4 — xG per shot — **DROPPED**
No shotmap exists.

### X5 — Trailing target-rate means — **ADOPTED**
Trailing target and conceded means are the count engines' base inputs.

### X6 — xGOT per shot — **DROPPED**
No xGOT or shotmap exists.

### X7 — Opp-box touches — **ADOPTED as corners ARM only**
The arm uses minimum-8 trailing means for box touches for/against and falls
back to Gate Zero when unavailable. Reliability is 0.388 for box-touches-for;
corner correlation is 0.469. Coverage ramps from 30.5% in 2023 to 100% in
2025, so the ramp is explicit rather than imputed.

### X8 — Referee yellow rate — **ADOPTED as cards ARM only**
Strictness r=0.379 at ≥10 refereed matches. Missing referee falls back to Gate
Zero; there is no imputation. The ≥20 screen is not estimable because only
one referee reaches it.

### X9 — Reference territorial covariates — **ADOPTED**
Production corners covariates are possession and big chances and are part of
Gate Zero, as in the sibling architecture.

## §2 Architectural components

Ratings, home advantage, Dixon-Coles rho, NB sizes, the v5 ratio component,
league base rates, and half-share constants are fitted/reference components,
not covariates.

## §3 Rejected list

Halves modelling, finishing/form, absence/lineup, post-match snapshots,
conference features (no conference field exists), imported tier offsets,
conversion/on-target-rate form, and any non-pre-match feature are rejected.

## §4 Halves constants (frozen, presentation only)

| market | 1H share |
|---|---:|
| goals | 0.468 |
| SOT | 0.465 |
| corners | 0.469 |
| total shots | 0.461 |
| yellow cards | 0.373 |

## §5 Consumption map

| Candidate | Base inputs | Variant-arm features |
|---|---|---|
| G-USLL1 | X1 goals-only | SHR thin-team shrinkage |
| S-USLL1 | X5 + v5 architecture | RS ratio prior |
| C-USLL1 | X5 + X9 | X7 box-touch multiplier |
| K-USLL1 | X5 | X8 referee covariate |
| T-USLL1 | X5 + shots architecture | B level layer; C E9 trailing-r |

The goals-for split-half r≈0 caveat is material: it is noise in this league,
but DC remains Gate Zero by program rule. Reliability gates FEATURES; it does
not rewrite the reference pattern.

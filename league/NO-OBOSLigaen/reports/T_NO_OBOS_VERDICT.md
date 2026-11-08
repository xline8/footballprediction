# T-NO-OBOS verdict — total shots

**FAIL at the virgin legs. Nothing ships.**

Reference: the shots family (NO-Eliteserien engine). Primary line
20.5. Prereg: `prereg/PREREG_T_NO_OBOS.md` (tuning 2022, gate pool
2023–2025). FT-only market (no halves source). Built ahead of the
top-5 prospective verdict under the user order recorded for T-J1;
that trial is untouched.

## Dev (gate pool 2023–2025, n=719 with target)

| Arm | LL@20.5 gate pool |
|---|---|
| A (v1 pattern) | 0.6678 |
| C (E9 trailing-r) | 0.6681 |
| League base rate | 0.6884 |
| Naive trailing-10 | 0.6897 |

Both arms beat both baselines → both passed the dev gate. Verified by
the coordinator as n-weighted means of the gate-pool season rows in
`engine/total_shots/results_dev.json` — exact agreement.

## Virgin (2026, read ONCE, n=237 with target)

| Arm | LL@20.5 | Mean P(over) | Actual | Cal. diff | SE |
|---|---|---|---|---|---|
| A | 0.6439 | 59.31% | 67.51% | −8.20pp | 3.04pp |
| C | 0.6446 | 59.16% | 67.51% | −8.35pp | 3.04pp |
| League base rate | **0.6403** | 60.91% | 67.51% | −6.60pp | 3.04pp |
| Naive trailing-10 | 0.6504 | 67.06% | 67.51% | −0.45pp | 3.09pp |

## Gate arithmetic

- Leg (i): LL ≤ arm A's (the reference) and ≤ best baseline's. Best
  baseline is the league base rate at **0.6403**; A scores 0.6439 and
  C 0.6446 → **both fail leg (i)**.
- Leg (ii): calibration breaches −8.20pp (A) / −8.35pp (C) against SE
  3.04pp → both fail (ii) as well, beyond one SE.

The 2026 virgin ran hot on shots (23.3/match, over-rate at 20.5 of
67.5% vs the dev's 48.3%) — the new-regime level (F9) kept rising and
both model arms, anchored to trailing team ratings, under-predicted
by ~8pp, while a constant prior-seasons base rate happened to sit
closer. The E9 trailing-r arm did not rescue the level problem (it
adjusts dispersion, not level). No rescue arm may be invented after
the fact.

## What ships

Nothing. Arm A's virgin predictions are exported as the record copy,
labelled arm A: `predictions/t_no_obos_virgin_predictions.csv`
(237 rows, FT ladder 19.5/20.5/21.5; coordinator-recomputed LL@20.5
0.6439, exact agreement).

# Verdict — K-CN (cards): **PROVISIONAL PASS** (Gate Zero ships)

Prereg: `prereg/PREREG_K_CN.md` (frozen and committed before fitting).
Primary line 3.5. Target: stats-feed yellows (frozen; the
stats-vs-events artefact is confined to the excluded 2021–2022 era).
Era 2023+; warm-up 2023; dev scored 2024+2025 (n = 480); virgin 2026
(n = 240). All numbers recomputed by the coordinator from the
per-match prediction CSVs against the league CSV.

## Dev (per-match walk-forward, predict-then-update; NB r from warm-up)

| Arm | Pooled LL@3.5 | 2024 | 2025 |
|---|---|---|---|
| Gate Zero | 0.6868 | 0.6833 | 0.6902 |
| League base rate | 0.6932 | — | — |
| Naive trailing-10 | 0.6956 | — | — |

Dev gate: Gate Zero beats both baselines (thin margins: −0.0064 /
−0.0088 LL) → virgin read.

## Virgin (2026, read once)

| Arm | LL@3.5 | Mean pred P(over) | Actual over-rate | Calibration (pp) | SE (pp) |
|---|---|---|---|---|---|
| Gate Zero | 0.6752 | 0.5343 | 0.5542 | +1.98 | 3.18 |
| League base rate | 0.6879 | — | — | — | — |
| Naive trailing-10 | 0.6928 | — | — | — | — |

## Gate arithmetic

- Leg (i) LL: 0.6752 ≤ best baseline 0.6879 ✓.
- Leg (ii) calibration: breach +1.98pp > 1.0pp boundary but within
  1 SE (3.18pp) → PROVISIONAL.

**K-CN PROVISIONAL PASS; Gate Zero ships**
(`predictions/k_cn_virgin_predictions.csv`, fitted params in
`engine/cards/fitted_params_virgin.json`; 1H/2H presentation via the
frozen yellow-cards constant 0.3328).

## Preregistered sensitivity (not a gate leg)

Against the event-feed virgin target (ev_yellow totals): LL@3.5 =
0.6726, calibration +3.65pp (SE 3.16pp) — the same provisional
reading; the stats-feed freeze does not drive the verdict.

# S-NO-OBOS verdict — shots on target

**FAIL at the virgin legs. Nothing ships.**

Reference: production `model_sot.py` v5 pattern (NO-Eliteserien engine
shape; NB r=79.94 frozen). Primary line 9.5. Prereg:
`prereg/PREREG_S_NO_OBOS.md`. FT-only market (no halves source).

## Dev (walk-forward, warm-up 2021, scored 2022–2025, n=959)

| Arm | LL@9.5 pooled | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| Gate Zero | 0.6646 | 0.7105 | 0.5617 | 0.6795 | 0.7070 |
| RS | 0.6652 | 0.7111 | 0.5598 | 0.6806 | 0.7096 |
| Base rate | 0.7175 | | | | |
| Naive trailing-10 | 0.6800 | | | | |

Both arms beat both baselines → both passed the dev gate and were
read on the virgin. Recomputed by the coordinator from
`engine/sot/results_dev.csv` — exact agreement.

## Virgin (2026, read ONCE, n=237 with target)

| Arm | LL@9.5 | Mean P(over) | Actual | Cal. diff | SE |
|---|---|---|---|---|---|
| Gate Zero | 0.7010 | 0.5518 | 0.5148 | +3.70pp | 3.27pp |
| RS | 0.6984 | 0.5535 | 0.5148 | +3.87pp | 3.26pp |
| Base rate | 0.6987 | 0.4603 | 0.5148 | −5.45pp | 3.25pp |
| Naive trailing-10 | 0.7069 | 0.5402 | 0.5148 | +2.54pp | 3.29pp |

Recomputed by the coordinator from `engine/sot/virgin_rows.csv` —
exact agreement.

## Gate arithmetic (per arm)

- **Gate Zero**: leg (i) LL ≤ best baseline — 0.7010 > 0.6987 (base
  rate) → **fails (i)**. Leg (ii): |+3.70pp| > 1.0pp and > 1 SE
  (3.27pp) → fails (ii) as well.
- **RS**: leg (i) — 0.6984 ≤ Gate Zero's 0.7010 and ≤ best baseline
  0.6987 (by 0.0003) → passes (i). Leg (ii) — |+3.87pp| > 1.0pp and
  > 1 SE (3.26pp) → **fails (ii)** (not within one SE, so not even
  provisional). Leg (iii) sign check — RS dev LL ≤ GZ in only 1 of 4
  dev seasons (2023) → fails (iii) as well.

No arm passes all virgin legs → **FAIL**. The virgin season's SOT
level (9.77/match) sat between the feed's two counting regimes and
both model arms over-predicted the over-rate by ~4pp; the frozen
r=79.94 dispersion is visibly too tight for this league's
overdispersed SOT (pooled dispersion 1.92, EDA F2/F9) — recorded as
the likely mechanism, not as a rescue: no arm may be invented after
the fact.

## What ships

Nothing. The Gate Zero virgin predictions are exported as the record
copy, labelled arm GZ with `ships: false` in
`engine/sot/fitted_params_virgin.json`:
`predictions/s_no_obos_virgin_predictions.csv` (237 rows, FT ladder
8.5/9.5/10.5).

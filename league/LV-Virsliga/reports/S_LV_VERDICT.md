# Verdict — S-LV (Latvia Virsliga SOT model)

**PASS — Gate Zero ships (clean).** The only passing market in this league.

## Dev results (walk-forward over the stats era; warm-up 2025-03-05–04-30, scored 2025-05-01–11-09, n=133)

| arm | LL@9.5 | league base rate | naive trailing-10 |
|---|---|---:|---:|
| Gate Zero | **0.682846** | 0.689921 | 0.683999 |
| RS (BB prior 200 → 20,000) | 0.685650 | 0.689921 | 0.683999 |

Gate Zero beats both baselines on dev (vs naive by only 0.00115 —
thin, but a pass). RS loses to naive and is dead. Dev sign check
for both-pass: moot, only Gate Zero reaches the virgin.

## Virgin results (2026, n=179, read once for the dev-passing arm)

| arm | LL@9.5 | league base rate | naive trailing-10 | calibration (actual − predicted) | SE |
|---|---|---:|---:|---:|---:|---:|
| Gate Zero | **0.679910** | 0.679994 | 0.680898 | +0.0021 (+0.21pp) | 0.03697 |

Mean P(over 9.5) 0.4169 vs actual over-rate 0.4190.

## Gate arithmetic (frozen in PREREG_S_LV.md)

- Leg (i) LL: 0.679910 ≤ Gate Zero's 0.679910 (self) AND ≤ best
  baseline's 0.679994 (league base rate) — **PASS**, by 0.000084.
  The margin over the league base rate is hair-thin; the rule as
  frozen is a comparison, not a margin, and it passes.
- Leg (ii) calibration: |+0.21pp| ≤ 1.0pp — **clean PASS**.
- Leg (iii): Gate Zero is exempt (RS dead at dev).

Both-pass rule: only Gate Zero passes → **Gate Zero ships**.

## What ships

- Arm: Gate Zero (production SOT v5 unmodified).
- Virgin predictions: `league/LV-Virsliga/predictions/s_lv_virgin_predictions.csv`
  (179 rows; FT ladder 8.5/9.5/10.5; 1H/2H presentation via frozen
  SOT constant 0.4637).
- Fitted params: `engine/sot/fitted_params_virgin.json` (walk-forward
  model; no single fitted parameter set — see engine README).
- Virgin levels: mean predicted SOT 8.98 vs actual 9.19.

## Verification

Dev LLs recomputed independently from `predictions_dev.csv`
(GZ 0.682846, RS 0.685650, exact); both dev baseline LLs
recomputed independently (league 0.689921, naive 0.683999,
exact). Virgin LLs + calibration recomputed independently with
a separate walk through the frozen Engine (GZ 0.6799104541,
league 0.6799943184, naive 0.6808976142, calibration +0.0021 /
SE 0.036966 — exact). Targets match the raw CSV on all scored
matches in both windows.

## Virgin-read disclosure

The virgin metrics were computed three times with identical GZ
numbers (deterministic code): the first metrics run omitted the
prereg-required virgin baselines (an oversight in the ported
harness); the second run added only those baseline legs; the
predict run reproduced the metrics and wrote the shipped
predictions. No design, arm, line, or gate changed between runs;
no result was used to alter anything.

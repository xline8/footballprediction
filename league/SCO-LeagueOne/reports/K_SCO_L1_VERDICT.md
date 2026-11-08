# Verdict — K-SCO-L1 (Scotland League One cards)

**FAIL at both virgin legs. Nothing ships.**

Prereg: `prereg/PREREG_K_SCO_L1.md`. Primary line 3.5, Gate Zero
only. Target: total event Yellow cards (`yellow_home +
yellow_away`; the stats feed carries no `yellow_cards` key in any
of the 969 payloads, so the event count is the target by
construction; `YellowRed` events are not yellows). Dev n=540,
virgin 2025/2026 n=180. All numbers recomputed by the builder from
the per-match prediction CSVs and by an independent replay of the
Online state (r values, LLs and per-match means all reproduced to
full printed precision). Calibration = actual − predicted.

## Dev

Pooled LL@3.5 **0.6846**, beating both baselines (league base
rate 0.6937; naive trailing-10 0.6948) — dev gate PASS. Per-season
LL@3.5, model vs base vs naive: 2022/2023 0.6888 vs 0.6937 vs
0.7019; 2023/2024 0.6858 vs 0.6960 vs 0.6916; 2024/2025 0.6791 vs
0.6915 vs 0.6908 — the model beats both baselines in all three dev
seasons. Dev NB sizes (estimated once from the 2021/2022 warm-up
predictions): model r = 30.39, base r = 50.85, naive r = 58.07.

## Virgin

- LL@3.5 **0.65452** vs baselines 0.69000 (league base rate) /
  0.63761 (naive) — the model beats the base rate but loses to the
  naive trailing-10: leg (i) **FAIL**.
- Calibration: mean P(over 3.5) 0.5313 vs actual over-rate 0.6056
  → breach **+7.42pp** (actual − predicted), SE 3.55pp — far
  beyond 1pp + 1 SE: leg (ii) **FAIL**.

The virgin season was the most card-heavy in the corpus (event
yellows 4.13/match vs the dev-era 3.53–3.64 and the seed season's
3.62; over-3.5 rate 0.606 vs dev 0.469). The naive trailing-10
adapts to the level shift faster than the decayed team-rating
model, which is why it wins the virgin LL leg while losing dev.
Team yellow ratings are this league's weaker count trait
(split-half r 0.388 / 0.535, below the goals traits). Virgin NB
sizes (re-estimated once from all pre-virgin warm-up predictions,
n=720): model r = 64.32, base r = 67.85, naive r = 56.74.
**K-SCO-L1 is FAIL. Nothing ships.** `fitted_params_virgin.json`
is `{}` and no `predictions/k_sco_l1_virgin_predictions.csv` was
written, as the prereg requires on FAIL.

No fitted params, no predictions. Production code untouched.

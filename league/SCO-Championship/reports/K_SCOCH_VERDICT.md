# Verdict — K-SCOCH (Scotland Championship cards)

**FAIL at both virgin legs. Nothing ships.**

Prereg: `prereg/PREREG_K_SCOCH.md`. Primary line 3.5, Gate Zero
only. Target: unified yellows (event-feed Yellow count; the stats
feed carries yellow_cards in only 19 of 969 payloads, and on
those 19 the two sources agree exactly — EDA artefact check).
Dev n=540, virgin 2025/2026 n=180. All numbers recomputed by the
coordinator from the per-match prediction CSVs. Calibration =
predicted − actual.

## Dev

Pooled LL@3.5 **0.6897**, beating both baselines (league base
rate 0.6926; naive trailing-10 0.6993) — dev gate PASS.

## Virgin

- LL@3.5 **0.66784** vs baselines 0.65931 (league base rate) /
  0.66385 (naive) — the model is worse than BOTH baselines:
  leg (i) **FAIL**.
- Calibration: mean P(over 3.5) 0.5791 vs actual over-rate
  0.6556 → breach **−7.64pp**, SE 3.59pp — far beyond 1pp + 1 SE:
  leg (ii) **FAIL**.

The virgin season was the most card-heavy in the corpus (event
yellows 4.34/match vs the dev-era 3.66–4.26 and the seed season's
3.21; over-3.5 rate 0.656 vs dev 0.541). Team yellow ratings are
also this league's weakest count trait (split-half r 0.301 /
0.231). **K-SCOCH is FAIL. Nothing ships.**

# Verdict — G-IE (Ireland Premier Division goals) — **FAIL** (virgin calibration leg, OU 2.5)

Prereg: `prereg/PREREG_G_IE.md`. Goals-only Dixon-Coles (IE xG
exists only in 2025–2026, so the blend was frozen out before
fitting). Arms: Gate Zero + SHRINK.

## Dev (season-blocked walk-forward, eval 2022–2025, n = 720)

| | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | **1.0256** | **0.2089** | **0.6900** |
| SHRINK | 1.0256 | 0.2089 | 0.6900 |
| Climatology | 1.0788 | 0.2262 | 0.6909 |

Gate Zero passes the dev gate on all three metrics (the OU margin
is thin: 0.0009). SHRINK is numerically identical to Gate Zero in
every dev season — under season-blocked fits a promoted club has 0
prior in-league matches at fit time, so the n/6 shrinkage (which
bites only at 1–5 prior matches) never engages. The arm is a
no-op here by construction, recorded plainly.

## Virgin (2026, n = 180, read ONCE for both dev-passing arms)

| | 1X2 LL | HW calib (SE) | OU2.5 calib (SE) |
|---|---|---|---|
| Gate Zero / SHRINK | 1.0515 | +2.60pp (3.51) | **−11.80pp (3.72)** |
| Climatology | 1.0902 | — | — |

(Independently recomputed from the predictions CSV: LL 1.0515,
OU diff −0.1180 / SE 0.0372, HW diff +0.0260 / SE 0.0351 — exact.)

- Leg (i) LL: PASS (1.0515 ≤ climatology 1.0902).
- Leg (ii) calibration: home-win +2.60pp is inside the provisional
  band (≤ 1pp + 1 SE = 4.51pp), but OU 2.5 is −11.80pp against a
  1 SE band of 4.72pp — **FAIL, beyond 1 SE**. 2026 was a
  high-scoring season (2.81 goals/match, over-2.5 rate 52.8%)
  after the low 2024 season (2.27) dragged the decay-weighted fit
  down (mean predicted over-rate 41.0%).

**FAIL.** Nothing ships. Per the prereg, Gate Zero's virgin
predictions are still written to
`predictions/g_ie_virgin_predictions.csv` and labelled here as
non-shipped.

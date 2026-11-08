# Verdict — G-BD (Bangladesh Football League goals, Dixon–Coles goals-only)

**FAIL — Gate Zero passes two of the three dev legs (1X2 LL, RPS) but fails
the OU2.5 LL leg decisively in every dev season. Per the frozen prereg rule
(PREREG_G_BD.md), Gate Zero failing dev makes the variant arms moot and the
virgin is NOT read. Nothing ships.**

## Dev (season-blocked walk-forward; seed 2022/2023, 95 finished matches — rounds 4–22 only; pooled n = 270)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.0482 | 0.2084 | 0.7731 |
| SHRINK | 1.0482 | 0.2084 | 0.7731 |
| Climatology | 1.0985 | 0.2330 | 0.6946 |
| Naive trailing-10 | 1.1127 | 0.2204 | 0.7886 |

Per-season Gate Zero vs climatology (1X2 LL / RPS / OU2.5 LL):

| Season | n | Gate Zero | Climatology |
|---|---|---|---|
| 2023/2024 | 90 | 0.9903 / 0.1876 / 0.7241 | 1.1121 / 0.2256 / 0.6941 |
| 2024/2025 | 90 | 1.1660 / 0.2482 / 0.8583 | 1.0897 / 0.2446 / 0.6913 |
| 2025/2026 | 90 | 0.9885 / 0.1895 / 0.7368 | 1.0939 / 0.2289 / 0.6985 |

Gate arithmetic (PREREG_G_BD): pooled 1X2 LL beats climatology ✓ (1.0482 <
1.0985); pooled RPS beats climatology ✓ (0.2084 < 0.2330); pooled OU2.5 LL
beats the base-rate baseline ✗ (0.7731 > 0.6946). **Dev gate FAILS on the
OU2.5 leg for both arms.** The failure is in all three seasons, not a pooled
artefact: the model loses the OU2.5 leg to climatology by 0.030, 0.167, and
0.038 respectively. SHRINK is byte-identical to Gate Zero in every season
(0 changed rows, 0 thin-history teams), exactly as EDA F13 predicted: no team
falls in the 1–5 prior-match band at any target-season start.

## Virgin

**Not read.** `results_virgin.json` records `{"virgin_read": false}` with the
reason "gate zero failed dev gate; virgin not read (variants moot)". The
2026/2027 window (29 matches, in progress) remains untouched; its season-end
confirmatory read does not apply because no arm passed dev.

## Why it failed (diagnosis, not a rescue)

- The failure is a totals-discrimination failure, not a totals-level miss.
  Mean predicted P(over 2.5) tracks the actual over-rate per season (0.515 vs
  0.544; 0.535 vs 0.533; 0.513 vs 0.456), but the per-match predictions are
  uncorrelated with actual overs: pooled corr −0.031 (per-season −0.031,
  −0.146, +0.079), mean predicted over-probability 0.517 on actual overs vs
  0.526 on actual unders. The predicted over-probability spans 0.24–0.97
  (sd 0.156) — confident variation that carries no signal. The Brier score
  for over 2.5 is 0.264–0.306 per season vs climatology's 0.248–0.249.
- The outcome dimension works: home-win predictions correlate 0.350 with
  actual home wins (mean predicted 0.493 on actual home wins vs 0.326
  otherwise), and the 1X2 LL and RPS legs pass. The ratings separate winners
  from losers but do not separate high-total from low-total matches in this
  league.
- Contributing context: fitted home advantage in the final dev fit is
  h = −0.004 — effectively no home edge (dev home-win 0.375 vs away-win
  0.348) — and the 2024/2025 season is the worst (model 1X2 LL 1.1660 also
  loses to climatology that season). The thin dev windows (F14, n=270) make
  the pooled OU2.5 gap of 0.0784 hard to attribute to a single cause, but the
  per-season consistency of the OU2.5 loss rules out a one-season fluke.

## Verification (independent of the engine)

- Pooled metrics recomputed from the per-match `results_dev.csv` reproduce
  `results_dev.json` exactly (LL 1.0482, RPS 0.2084, OU 0.7731; climatology
  1.0985 / 0.2330 / 0.6946); per-match LL values recomputed from the stored
  probabilities match to 6 decimals.
- The engine's DC fit was cross-checked against production `model_v2.py`'s
  `DC` on the identical 2025/2026 training set (275 matches before
  2025-09-26, hl=270): attack/defence ratings identical (max diff 0.0),
  rho −0.10 in both, h −0.0037 in both, match probabilities identical to
  <5e-11. The FAIL is genuine, not a harness bug.
- No 2026/2027 row appears in any dev artefact.

## What ships

Nothing. No virgin predictions file, no fitted-params file. G-BD verdict is
FAIL; S/C/K/T are not buildable (PREREG_NOT_BUILDABLE_SCKT_BD.md). League
score: **0 pass / 1 fail / 4 not buildable.**

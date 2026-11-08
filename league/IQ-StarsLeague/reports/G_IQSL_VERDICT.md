# Verdict — G-IQSL (Iraq Stars League goals): **FAIL (dev gate)**

Frozen decision: `PREREG_G_IQSL.md` (prereg commit 8eed0f37, before any
fitting). **Virgin 2025/2026 was NOT read.** Confirmatory 2026/2027
untouched. Nothing ships.

## Dev (season-blocked walk-forward; seed 2021/2022, scored 2022/2023–2024/2025, n = 1,104)

Reference: production Dixon–Coles, goals-only, half-life 270 days, rho
grid 0/−0.05/−0.10/−0.15, tau correction. Fit scope per scored season:
all regular matches dated strictly before that season's first match.
Independently verified: the production `model_v2.py` DC replayed from
scratch reproduces the engine's per-season 1X2 LL and OU2.5 LL exactly
(≤0.000001) for all three scored seasons, including fitted h
(0.3089 / 0.1988 / 0.0767) and rho (−0.15 in all three).

| season | n | Gate Zero 1X2 LL | Clim 1X2 LL | Gate Zero RPS | Clim RPS | Gate Zero OU2.5 LL | Clim OU2.5 LL | Gate Zero OU calib pp (SE) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022/2023 | 355 | 1.0481 | 1.0918 | 0.2068 | 0.2207 | 0.7221 | 0.6800 | −6.48 (2.68) |
| 2023/2024 | 369 | 1.0390 | 1.1064 | 0.2007 | 0.2222 | 0.6850 | 0.6768 | −5.55 (2.56) |
| 2024/2025 | 380 | 1.0287 | 1.0883 | 0.2111 | 0.2305 | 0.6790 | 0.6699 | −0.25 (2.53) |
| **Pooled** | **1,104** | **1.0384** | **1.0955** | **0.2063** | **0.2246** | **0.6949** | **0.6754** | **−4.03 (1.50)** |

SHRINK pooled is identical to Gate Zero to all reported decimals
(1.0384 / 0.2063 / 0.6949), in every season. This is not a bug: the
arm is inactive by construction in this league — no club enters a
scored season with 1–5 prior in-league matches (new clubs have 0 and
start at the league mean in both arms; every returning club has ≥34).
So SHRINK ≡ Gate Zero here, and its dev verdict is the same.

## Gate arithmetic (mechanical, per prereg)

Dev gate requires pooled 1X2 LL AND RPS AND OU2.5 LL all to beat
climatology:

- 1X2 LL: 1.0384 < 1.0955 — PASS (by 0.0571).
- RPS: 0.2063 < 0.2246 — PASS (by 0.0183).
- OU2.5 LL: 0.6949 > 0.6754 — **FAIL** (worse by 0.0194, and worse in
  every scored season individually).

Gate Zero fails the dev gate, so per the frozen rule **G-IQSL FAILS**,
variants are moot, and the virgin is not read. Pooled home-win
calibration (−0.62pp, SE 1.41) would have passed 1pp, but calibration
is a virgin leg and is never reached.

## Why the OU leg fails

Goals drifted upward across dev (regular goals/match 1.98 → 2.18 →
2.30 → 2.26; EDA F1) while the expanding-window DC, even with a 270-day
half-life, under-predicts the over-rate: pooled OU calibration −4.03pp
(−6.48pp and −5.55pp in the first two scored seasons). Climatology's
prior-season over-rate tracks the drift better on this leg, so the
plain base rate beats the model on OU2.5 log loss even though the
model clearly beats it on 1X2 outcomes. The gap narrowed in 2024/2025
(OU calibration −0.25pp) but the OU LL leg still lost (0.6790 vs
0.6699). No rescue arm is permitted: the prereg forbids post-hoc arms,
and the failure is a complete outcome.

## What ships

Nothing. No predictions CSV, no fitted params, no daily-pipeline
entry. If FotMob's Iraq feed later gains xG/stats (or the goals drift
stabilises), the candidate needs a fresh prereg over the new data;
nothing in this build pre-registers it.

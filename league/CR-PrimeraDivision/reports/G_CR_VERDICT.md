# Verdict — G-CR (Costa Rica Primera Division goals model)

**Verdict: FAIL — dev gate (OU2.5 leg). Virgin NOT read. Nothing ships.**

Prereg: `league/CR-PrimeraDivision/prereg/PREREG_G_CR.md` (frozen 2026-11-10, before any fitting).
Engine: `league/CR-PrimeraDivision/engine/goals/`. Results: `engine/goals/results_dev.json` (+ CSV).
Single arm: Gate Zero (unmodified production Dixon-Coles, goals-only — no xG exists in this league).

## Dev results (regular season, season-blocked walk-forward)

| Season | n | | LL 1X2 model | LL 1X2 climatology | RPS model | RPS climatology | OU2.5 LL model | OU2.5 LL climatology |
|---|---|---|---|---|---|---|---|---|
| 2022/2023 | 228 | | 0.9826 | 1.0491 | 0.2016 | 0.2245 | 0.7102 | 0.6904 |
| 2023/2024 | 264 | | 0.9551 | 1.0574 | 0.1922 | 0.2279 | 0.7224 | 0.6913 |
| **Pooled** | **492** | | **0.9678** | **1.0536** | **0.1965** | **0.2263** | **0.7167** | **0.6909** |

## Gate arithmetic (mechanical, per prereg)

- 1X2 LL leg: 0.9678 < 1.0536 — **PASS** (model beats climatology by 0.086).
- RPS leg: 0.1965 < 0.2263 — **PASS** (beats climatology by 0.030).
- OU2.5 LL leg: 0.7167 > 0.6909 — **FAIL** (model is worse than the base over-rate by 0.026,
  in both dev seasons individually: 0.7102 vs 0.6904 and 0.7224 vs 0.6913).

Dev gate requires all three legs. The arm is dead at dev. Per the frozen prereg, **the virgin window
(2024/2025) was NOT read** — there is no virgin table, no virgin predictions file, and no fitted
params for G-CR. Its absence is itself recorded here, as the prereg requires.

## Diagnosis (dev data only — no rescue arm is permitted by the prereg)

The model is good at outcomes and bad at totals. The failure is a level lag, not a code error:

- `dc.probs()` verified against scipy: P(over 2.5) at λ = 1.33/1.33 is 0.4965 in both.
- Climatology OU LL recomputed by hand from the levels table: 0.6904 / 0.6913 / 0.6909 — matches the
  harness exactly.
- Mean predicted P(over 2.5) was 0.492 (2022/23) and 0.496 (2023/24) against actual over-rates of
  0.553 and 0.530. Mean fitted lambda totals were 2.66 / 2.67 against actual 2.89 / 2.69 goals per
  match. The decayed fit (half-life 270 days) lags scoring-level shifts: 2022/23 jumped to 2.89 goals
  after a 2.73 season, and the model kept pricing the old level. Shrinking P(over 2.5) toward 0.5
  (diagnostic only) improves OU LL to 0.697 / 0.704 — the probabilities are mis-levelled, not merely
  overconfident.
- The 1X2/RPS wins show the ratings carry real signal (consistent with EDA F2, goals traits r ≈ 0.79);
  the failure is specific to the totals leg of the gate, which is a hard leg.

No post-hoc arm, shrinkage, or re-leveling was attempted: the prereg forbids rescue arms, and the
gate was never moved after results were seen.

## What ships

Nothing. G-CR does not ship. The league's goals product stays unbuilt; a future retry would need a
new pre-registration (e.g. a level-tracking variant arm), not a patch to this verdict.

# G-FO Verdict — Faroe Islands Premier League goals model

Date: 2026-11-10. Branch `build/fo-premier-league`. Prereg:
`league/FO-PremierLeague/prereg/PREREG_G_FO.md` (commit 4c162d84,
frozen before any fitting). Engine:
`league/FO-PremierLeague/engine/goals/`. Implementation by Codex
(gpt-5.6-luna) under the two-agent flow; all numbers below were
reproduced end-to-end by the coordinator's own rerun of the dev
harness (identical to the last digit), recomputed from the per-match
`results_dev.csv`, and the DC code was diffed against the J1
reference (goals-only adaptation only: same tau, 14 sweeps, damping
0.7, +0.25 smoothing, HL 270).

## Verdict: FAIL — no arm passes the dev gate, nothing ships

Both arms beat climatology decisively on 1X2 log-loss and RPS, but
both LOSE the OU2.5 log-loss leg to climatology, so both fail the
dev gate and the virgin window (2026) is NOT read. The model is
good at who wins and bad at how many goals — in a 10-team league
where the total-goals level swings season to season (3.63, 3.28,
3.15, 3.30, 3.63 in dev; 2.82 in virgin 2026), the expanding
climatology total is the harder total to beat.

## Dev results (walk-forward expanding, season-blocked; n = 539)

Climatology per season uses pooled prior seasons only; the pooled
climatology row is the pooled score of those per-season predictions.
Fitted `h`/`rho` per target season (same fit for both arms; SHRINK
scales the fitted ratings by 0.85 after the fit): 2022 h=0.114,
rho=−0.10; 2023 h=0.086, rho=0.0; 2024 h=0.150, rho=−0.10; 2025
h=0.202, rho=0.0.

| Season | n | Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|---|---|
| 2022 | 134 | Gate Zero | 0.9107 | 0.1912 | 0.6956 |
| 2022 | 134 | SHRINK | 0.9000 | 0.1894 | 0.6952 |
| 2022 | 134 | Climatology | 1.0366 | 0.2443 | 0.6778 |
| 2023 | 135 | Gate Zero | 0.7789 | 0.1548 | 0.6994 |
| 2023 | 135 | SHRINK | 0.7683 | 0.1539 | 0.6820 |
| 2023 | 135 | Climatology | 1.0138 | 0.2421 | 0.6803 |
| 2024 | 135 | Gate Zero | 0.6829 | 0.1365 | 0.6190 |
| 2024 | 135 | SHRINK | 0.7056 | 0.1405 | 0.6412 |
| 2024 | 135 | Climatology | 0.9780 | 0.2411 | 0.6214 |
| 2025 | 135 | Gate Zero | 0.8604 | 0.1707 | 0.6272 |
| 2025 | 135 | SHRINK | 0.8601 | 0.1718 | 0.6569 |
| 2025 | 135 | Climatology | 1.0673 | 0.2429 | 0.6041 |
| Pooled | 539 | Gate Zero | 0.8080 | 0.1633 | 0.6602 |
| Pooled | 539 | SHRINK | 0.8084 | 0.1638 | 0.6688 |
| Pooled | 539 | Climatology | 1.0239 | 0.2426 | 0.6458 |

Dev gate (pooled 1X2 LL and RPS must beat climatology, OU2.5 LL
must beat the base-rate baseline): Gate Zero **FAIL** — wins the
1X2 legs by a wide margin (0.8080 vs 1.0239; RPS 0.1633 vs 0.2426)
but loses OU2.5 (0.6602 vs 0.6458). SHRINK **FAIL** on the same leg
(0.6688 vs 0.6458). The OU2.5 failure is not close in any season
except 2024, where Gate Zero beats climatology by 0.24pp
(0.6190 vs 0.6214); in 2022, 2023 and 2025 it loses by 1.8pp,
1.9pp and 2.3pp.

Why the model loses on totals while winning on outcomes: the DC
ratings separate teams well (hence the 1X2 win), but the fitted
total level is set by the decay-weighted training window, and the
league's season-to-season total swings ±0.25 goals/match around it.
Climatology's pooled over-rate adapts to the same swings with no
fitted level at all. SHRINK does not rescue the leg — it moves the
OU2.5 LL the wrong way in 2024 and 2025.

## Virgin: NOT READ

No arm passed the dev gate, so per the prereg the virgin window
(2026, n = 135) is deliberately unread. `results_virgin.json`
records `{"virgin_read": false, ...}`. For the record only: the
virgin season ran cold (2.82 goals/match, OU2.5 over-rate 0.541 vs
dev 0.659), so a virgin read would very likely have failed the
calibration leg as well — but that is not a result, it is a
design-level observation, and no virgin number is computed or
reported here.

## Per-leg verdicts

| Leg | Gate Zero | SHRINK |
|---|---|---|
| Dev gate | FAIL (OU2.5 leg) | FAIL (OU2.5 leg) |
| Virgin LL | not read | not read |
| Calibration | not read | not read |
| Per-season sign check (dev 1X2 LL ≤ Gate Zero in ≥2 of 4) | n/a (comparator) | would pass 3/4 (moot — dev gate failed) |
| **Overall** | **FAIL** | **FAIL** |

## Verification notes (coordinator, independent of Codex)

- Full harness rerun by the coordinator reproduces every model
  number above exactly (pooled and per-season).
- Per-match `results_dev.csv` (539 rows) recomputed independently:
  pooled 1X2 LL / RPS / OU2.5 LL match the JSON to 4 decimals for
  all three methods; probabilities sum to 1 on every row.
- Dev isolation confirmed in code: the dev path loads only seasons
  2021–2025 (asserted, 674 rows); season 2026 is never loaded.
  The awarded match 3822183 is excluded from every fit and scored
  set (2022 n = 134, not 135).
- DC code diffed against the J1 reference: identical update rule,
  tau correction, rho grid and sweep count; the only differences
  are the goals-only observation (no xG branch — correct, no xG
  exists) and an added `assert date < cutoff` in the fit.
- No fitted virgin parameters exist (no virgin fit was run); no
  predictions CSV is written. Nothing ships.

# Verdict — G-LV (Latvia Virsliga goals model)

**FAIL — dev gate.** Nothing ships. The virgin 2026 was NOT read.

## Dev results (season-blocked walk-forward, seed 2021, scored 2022–2025, n=720)

| arm | season | 1X2 LL | RPS | OU2.5 LL |
|---|---|---:|---:|---:|
| Gate Zero | 2022 | 0.863581 | 0.175396 | 0.726785 |
| Gate Zero | 2023 | 0.913572 | 0.173738 | 0.710468 |
| Gate Zero | 2024 | 0.879942 | 0.183073 | 0.697294 |
| Gate Zero | 2025 | 0.928836 | 0.185251 | 0.700974 |
| Gate Zero | **pooled** | **0.896483** | **0.179365** | **0.708880** |
| Climatology | pooled | 1.060773 | 0.238049 | 0.694890 |

SHRINK is identical to Gate Zero on all 720 matches (0 differ):
every dev entrant is either fully unseen in training (0 prior
matches, fitted ratings already 0 — shrinking 0 changes nothing)
or a returnee with 36+ prior matches (shrink factor 1). The
sanctioned arm is vacuous in this league's dev window by
construction, not by implementation error (verified from
`fitted_params.json`: 2022 entrants Tukums/Auda/Super Nova have
counts absent and a = 0.0; MA-BotolaPro shows the same identical
arms).

## Gate arithmetic (frozen in PREREG_G_LV.md)

Dev gate requires pooled dev 1X2 LL and RPS to beat climatology
AND OU2.5 LL to beat the base-rate baseline:

- 1X2 LL: 0.896483 < 1.060773 — **PASS** (margin 0.164).
- RPS: 0.179365 < 0.238049 — **PASS** (margin 0.059).
- OU2.5 LL: 0.708880 > 0.694890 — **FAIL** (worse by 0.014).

The model beats climatology decisively on outcome probabilities
but loses on the total-goals line: the DC total-goals
distribution is worse than the expanding base over-rate in three
of four dev seasons (2022, 2024, 2025; only 2023 is marginally
better, 0.710468 vs 0.710546). Per the frozen rule — Gate Zero
fails dev ⇒ variants moot, virgin stays unread — the candidate
is FAIL and nothing ships. No rescue arm was invented; the gate
was not moved.

## What this means

The 1X2 signal is real (LL 0.90 vs 1.06 climatology) but the
OU2.5 leg is the binding constraint, as in most leagues in this
program (goals almost always fail at calibration/OU legs). The
failure is a complete, respectable outcome. Any future goals
attempt in this league needs a pre-registered design that
addresses the total-goals distribution, not the outcome
probabilities.

## Verification

Headline numbers recomputed independently from
`predictions_dev.csv` + the raw match CSV (separate script, not
the harness): pooled Gate Zero 0.896483 / 0.179365 / 0.708880 and
climatology 1.060773 / 0.238049 / 0.694890 — exact match to
`results_dev.json`. SHRINK-vs-Gate-Zero comparison: 0/720
predictions differ. Dev harness loads seasons 2021–2025 only
(asserted in code); no 2026 row was read.

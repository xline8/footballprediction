# Verdict — G-ID (goals): **FAIL** (dev gate; virgin deliberately unread)

Prereg: `prereg/PREREG_G_ID.md` (frozen before fitting). Gate Zero is
the production Dixon–Coles pattern, goals-only (no xG exists in this
league). Nothing ships.

## Dev results (season-blocked walk-forward; seed 2021/2022)

| season | arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|---|
| 2022/2023 | gate_zero | 1.1290 | — | 0.7639 |
| 2022/2023 | climatology | 1.0981 | — | 0.7007 |
| 2023/2024 | gate_zero | 1.0838 | — | 0.7206 |
| 2023/2024 | climatology | 1.0796 | — | 0.6959 |
| 2024/2025 | gate_zero | 1.0699 | — | 0.6943 |
| 2024/2025 | climatology | 1.0827 | — | 0.6944 |
| **pooled** | **gate_zero** | **1.0942** | **0.2325** | **0.7263** |
| **pooled** | **climatology** | **1.0868** | **0.2318** | **0.6970** |

(n = 918 dev matches. Pooled numbers recomputed independently from
`engine/goals/dev_predictions.csv`; they match the runner output.)

## Gate arithmetic (frozen legs)

Dev gate requires pooled 1X2 LL **and** RPS to beat climatology, and
OU2.5 LL to beat the base-rate baseline. Gate Zero fails all three:
1.0942 > 1.0868, 0.2325 > 0.2318, 0.7263 > 0.6970. **Gate Zero fails
dev ⇒ G-ID FAILS, the variant is moot, and the virgin season
(2025/2026) was NOT read** (`engine/goals/results_virgin.json`
records `virgin_read: false`).

Why it failed, plainly: the 2022/2023 scored season is predicted from
a fit on 2021/2022 only — the Bali-bubble season with no home
advantage (home−away goals −0.059) and the league's lowest goals
level (2.412). The following season restored normal home advantage
(+0.474) and level (2.761), so the fit under-predicted home wins and
overs for a full season (2022/2023 OU LL 0.7639 vs climatology
0.7007). By 2024/2025 Gate Zero does beat climatology (1.0699 vs
1.0827), but the pooled gate is the frozen rule and it is not close.
Dev calibration of Gate Zero (not a dev leg, reported for the
record): home-win breach −5.24pp (SE 1.67), OU2.5 breach −6.82pp
(SE 1.69) — under-prediction, same bubble-fit story.

## The shrink arm

`shrink` produced predictions identical to Gate Zero on all 918 dev
matches. This was audited and is **not** a wiring bug: the arm's code
path runs (verified in `engine/goals/arms.py` and the runner), but
under season-blocked fitting a team's prior-match count at any season
boundary is either 0 (new/promoted teams — whose DC ratings are
already the 0.0 league-mean default, and 0 × 0 = 0) or ≥34 (returning
teams — factor 1.0). The n/6 scale factor can therefore never bite in
this protocol. The variant is a mathematical no-op here and is in any
case moot after the Gate Zero dev failure. No rescue arm was invented
after the fact, per the prereg.

**G-ID: FAIL. Virgin unread. Nothing ships.**

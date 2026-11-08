# Phase 4 — Model Design: Poland I Liga Candidates

Stage 1 performs no fitting or evaluation. Calibration is actual minus predicted everywhere. Playoff rows are excluded from every fit and every gate.

## Feasibility

| Candidate | Status | Evidence |
|---|---|---|
| G-PL-ILiga goals | BUILDABLE | Gate Zero is the production DC pattern (model_v2.py); goals-only X1 is adopted. |
| S-PL-ILiga SOT | NOT BUILDABLE | stats 0/1,671 and shotmap 0/1,671 |
| C-PL-ILiga corners | NOT BUILDABLE | stats 0/1,671 |
| K-PL-ILiga cards | NOT BUILDABLE | no Yellow source; stats absent and events carry Red/YellowRed only |
| T-PL-ILiga total shots | NOT BUILDABLE | stats and shotmap absent |

Only G-PL-ILiga has a preregistration, engine, or virgin read. The four other markets have none.

## G-PL-ILiga

Gate Zero is the production DC pattern (model_v2.py) with goals-only X1. Candidate arms are Gate Zero and SHRINK, the sanctioned G-J2-lesson thin-data arm. An X2 arm is not allowed because FEATURES drops X2.

Development is season-blocked walk-forward, seed 2021/2022, scored 2022/2023–2024/2025 regular only (n=918). The primary line is OU2.5, with dev over-rate 0.497 from eda_numbers.json. Virgin is 2025/2026 regular only (n=306), read once after dev. 2026/2027 is TRANSITIONAL confirmatory, not read here.

The gate legs are verbatim from the frozen PL preregistration, with the
candidate name and phase rule adapted to this league: Dev gate — pooled dev
1X2 LL and RPS of an arm must beat climatology, and OU2.5 LL must beat the
base-rate baseline, else the arm is dead. Virgin legs — (i) LL leg: arm's
virgin 1X2 LL ≤ Gate Zero's AND ≤ climatology's; (ii) calibration leg:
|actual − mean predicted| ≤ 1.0pp pooled for home-win rate and for OU2.5
over-rate, SEs reported; a breach within 1 SE of the boundary is recorded
PROVISIONAL PASS, beyond it FAIL; (iii) per-season sign check on dev (arm LL
≤ Gate Zero LL in at least half the dev seasons) for the both-pass rule.
Both-pass rule: if Gate Zero and a variant both pass all legs, the lower
pooled virgin 1X2 LL ships; if only one passes, it ships; if none passes,
G-PL-ILiga verdict is FAIL and nothing ships. Ties go to Gate Zero.

Calibration is actual minus predicted everywhere. Playoff rows are excluded from every fit and every gate.


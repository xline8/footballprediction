# K-TR verdict — FAIL (nothing ships)

Prereg: `prereg/PREREG_K_TR.md` (frozen 06ad8d8, before fitting).
Primary line **4.5** (dev unified over-rate 0.436). Dev scored
2022/2023–2024/2025 (n = 1,033; seed 2021/2022). Target: unified
yellows (stats feed + frozen broken-stats event fallback, 47 rows).
Source: `engine/cards/results_dev.json`.

## Dev results — pooled LL@4.5

| arm | dev pooled LL@4.5 | league base | naive trailing-10 | dev gate |
|---|---:|---:|---:|---|
| Gate Zero | 0.697294 | 0.690967 | 0.698291 | **FAIL** (beats naive, not the league base rate) |
| X8 (referee) | 0.686474 | 0.690967 | 0.698291 | PASS (beats both; sign check 3/3 vs Gate Zero) |

## Gate arithmetic — why this is a FAIL despite X8

The prereg's frozen mechanical reading (inherited verbatim from the
program template) states: "Gate Zero dev failure ⇒ FAIL, virgin NOT
read." Gate Zero failed the dev gate, so the candidate fails as a
whole and no arm may ship, regardless of X8's dev strength.

## Disclosure — virgin read protocol breach (builder error, caught in coordinator verification)

The first builder run misread the mechanical rule, virgin-read X8 on
2025/2026 and produced shipping artifacts. Those numbers (virgin
LL@4.5 0.674013; calibration breach +2.208pp, SE 2.807pp — which would
have been a provisional pass under the virgin legs) are recorded here
for transparency ONLY: they are not a gate result, the virgin is
considered spoiled for K-TR, and the artifacts
(`predictions/k_tr_virgin_predictions.csv`,
`engine/cards/results_virgin.json`,
`engine/cards/fitted_params_virgin.json`) were removed by the
coordinator so nothing can be mistaken as shipped. (Referee coverage
was 50.0% in the 2021/2022 seed and 91.5% in the virgin season;
missing appointments fell back to Gate Zero with no imputation.)

## What survives

X8's dev evidence is the strongest referee signal in the program so
far (pooled dev LL 0.686474 vs Gate Zero 0.697294; strictness
reliability r ≈ 0.53 pooled, 30 referees with ≥20 matches) — the
referee trait is real in Türkiye. It simply cannot ship under this
prereg. A future candidate would need a NEW prereg with a fresh
virgin (2026/2027 once complete). Nothing ships from K-TR now.

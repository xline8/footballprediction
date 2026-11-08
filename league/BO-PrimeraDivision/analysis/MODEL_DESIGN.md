# Step 6 — Model design: BO-PrimeraDivision

No model is fit in this brief. This document freezes the feasible candidates, windows, lines, and gate arithmetic for a later preregistration.

## Feasibility and windows

| market | seed / training | dev scored | virgin / confirmatory | primary line |
|---|---|---|---|---|
| G-BO | 2021 regular, n=240 | 2022–2024 regular, n=896 | 2025 regular n=240; 2026 regular n=199 reserved confirmatory | OU 2.5 plus 1X2 |
| S/C/K/T-BO | 2025 rounds 1–10, n=80 | 2025 rounds 11–30, four expanding 5-round blocks, n=160 | 2026 transitional, n=199; season-end confirmatory read outstanding | 11.5 / 9.5 / 6.5 / 29.5 |

Count lines are computed only from the dev distribution: means and over-rates are SOT 11.2375 / 45.625% at 11.5, corners 9.5063 / 48.750% at 9.5, event-unified cards 6.1500 / 46.875% at 6.5, and total shots 29.8500 / 51.250% at 29.5. No 2026 value sets a line. There is no complete stats-era virgin season yet; 2026 is explicitly transitional.

## Candidates

G-BO is goals-only Dixon–Coles Gate Zero, with a pre-registered SHRINK arm for new-team/opening-match instability. Primary scoring is 1X2 log loss and RPS versus climatology, plus OU2.5 log loss versus the league base rate.

S-BO is Gate Zero v5 without xG inputs, plus an RS arm (Beta-Binomial prior 20,000 — the AU/SA-winning configuration). The RS arm is a robustness arm: EDA measures the on-target rate as a real trait here (split-half r=0.613), so RS is expected to lose and ships only if it beats Gate Zero on dev and virgin. C-BO is Gate Zero with X9 territory/chance inputs, plus an X7 box-touch variant arm. K-BO is Gate Zero only, with event-unified yellow targets; X8 is dropped. T-BO has arms A/B/C: v1, v2 level layer, and E9 trailing-r shots-family pattern.

Halves are FT plus 1H/2H presentation using the frozen constants in EDA; they are never separate fitted targets.

## Gate frame

The dev gate is pooled dev log loss at the primary line beating both baselines: the league base rate at that line and naive trailing-10. For goals, 1X2 LL and RPS must beat climatology, and OU2.5 LL must beat its base-rate baseline. If Gate Zero fails dev, variants are moot and the virgin is not read.

For a virgin leg, LL must be no worse than Gate Zero and both baselines. Calibration is `actual − predicted`; absolute mean calibration ≤1.0 percentage point is a clean PASS, a breach within 1 SE is PROVISIONAL PASS, and beyond that is FAIL. Variant arms require a per-block dev sign check. If multiple arms pass, the lower virgin LL ships; ties go to the simpler arm. A failed gate ships nothing.
